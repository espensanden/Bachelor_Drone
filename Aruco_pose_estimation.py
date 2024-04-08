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

    # While True loop starts here
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        np_frame = np.frombuffer(frame, dtype=np.uint8)
        img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)

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

        _, frame = cv2.imencode('.JPEG', img)
        server.wfile.write(b'--FRAME\r\n')
        server.send_header('Content-Type', 'image/jpeg')
        server.send_header('Content-Length', len(frame))
        server.end_headers()
        server.wfile.write(frame.tobytes())
        server.wfile.write(b'\r\n')

    # While True loop ends here

except Exception as e:
    logging.warning('An error occurred: %s', str(e))
finally:
    picam2.stop_recording()
