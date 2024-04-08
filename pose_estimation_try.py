import io
import logging
import socketserver
from threading import Condition
from http import server
import cv2
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import math
import time

found_count = 0
notfound_count = 0
first_run = 0



PAGE = """\
<html>
<head>
<title>Picamera MJPEG Streaming</title>
</head>
<body>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

cameraMatrix = np.array([[774.5585769798772, 0.0, 619.694166336029],
                         [0.0, 772.9641015632712, 352.49790332793935],
                         [0.0, 0.0, 1.0]])
distCoeffs = np.array([-0.3653858593342419, 0.1632243853386151, -0.002671633309837953, 0.00033826189145571927,
                       -0.038171194766151724])

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters_create()

horizontal_res = 640
vertical_res = 480

horizontal_fov = 62.2 * (math.pi / 180)  # Pi cam V1: 53.5 V2: 62.2
vertical_fov = 48.8 * (math.pi / 180)  # Pi cam V1: 41.41 V2: 48.8


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


def lander(frame):
    global first_run,notfound_count,found_count,start_time
    if first_run==0:
        print("First run of lander!!")
        first_run=1
        start_time=time.time()
    
    
    img = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    #if ids is not None:
        #cv2.aruco.drawDetectedMarkers(img, corners, ids)
    try:
        if ids is not None:
            ret = cv2.aruco.estimatePoseSingleMarkers(corners, 0.1, cameraMatrix, distCoeffs)
            (rvec, tvec) = (ret[0][0, 0, :], ret[1][0, 0, :])

            x = '{:.2f}'.format(tvec[0])
            y = '{:.2f}'.format(tvec[1])
            z = '{:.2f}'.format(tvec[2])

            y_sum = 0
            x_sum = 0

            x_sum = corners[0][0][0][0] + corners[0][0][1][0] + corners[0][0][2][0] + corners[0][0][3][0]
            y_sum = corners[0][0][0][1] + corners[0][0][1][1] + corners[0][0][2][1] + corners[0][0][3][1]

            x_avg = x_sum * .25
            y_avg = y_sum * .25

            x_ang = (x_avg - horizontal_res * .5) * (horizontal_fov / horizontal_res)
            y_ang = (y_avg - vertical_res * .5) * (vertical_fov / vertical_res)

            print("X CENTER PIXEL: " + str(x_avg) + " Y CENTER PIXEL: " + str(y_avg))
            print("MARKER POSITION: x=" + x + " y= " + y + " z=" + z)
            found_count=found_count+1
            print("Found count", found_count)
        else:
            notfound_count = notfound_count+1

    except Exception as e:
        print('Target likely not found. Error: '+str(e))
        notfound_count=notfound_count+1

    _, jpeg_frame = cv2.imencode('.JPEG', img)
    return jpeg_frame.tobytes()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    processed_frame = lander(frame)
                    end_time=time.time()
                    total_time=end_time-start_time
                    total_time=abs(int(total_time))
                    total_count=found_count+notfound_count
                    freq_lander=total_count/total_time
                    print("lander function had frequency of: "+str(freq_lander))
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(processed_frame))
                    self.end_headers()
                    self.wfile.write(processed_frame)
                    self.wfile.write(b'\r\n')

            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
picam2.hflip = True
picam2.vflip = True
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()
