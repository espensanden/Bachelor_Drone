import cv2
import numpy as np
import math
from picamera2 import Picamera2

id_to_find = 0
marker_size = 10 #in cm

now_landing = 0

cameraMatrix = np.array([[774.5585769798772, 0.0, 619.694166336029],
                         [0.0, 772.9641015632712, 352.49790332793935],
                         [0.0, 0.0, 1.0]])
distCoeffs = np.array([-0.3653858593342419, 0.1632243853386151, -0.002671633309837953, 0.00033826189145571927,
                       -0.038171194766151724])

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters_create()

#Camera
horizontal_res = 640
vertical_res = 480
picam2 = Picamera2()
picam2.preview_configuration.main.size = (horizontal_res,vertical_res)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()


horizontal_fov = 62.2 * (math.pi / 180 )  # Pi cam V2: 62.2
vertical_fov = 48.8 * (math.pi / 180)     # Pi cam V2: 48.8


def landing_drone():
    while True:
        im = picam2.capture_array()
        frame_np = np.array(im)
        #if not ret:
            #print("Failed to capture frame")
            #break

        gray = cv2.cvtColor(frame_np, cv2.COLOR_BGR2GRAY)
        ids = ''
        corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        
        try:
            if ids is not None and ids[0] == id_to_find:
                ret  = cv2.aruco.estimatePoseSingleMarkers(corners, 0.1, cameraMatrix, distCoeffs)
                (rvec, tvec) = (ret[0][0, 0, :], ret[1][0, 0, :])
                        
                x = '{:.2f}'.format(tvec[0])
                y = '{:.2f}'.format(tvec[1])
                z = '{:.2f}'.format(tvec[2])

                y_sum = 0
                x_sum = 0

                x_sum = corners[0][0][0][0]+ corners[0][0][1][0]+ corners[0][0][2][0]+ corners[0][0][3][0]
                y_sum = corners[0][0][0][1]+ corners[0][0][1][1]+ corners[0][0][2][1]+ corners[0][0][3][1]


                x_avg = x_sum*.25
                y_avg = y_sum*.25

                x_ang = (x_avg - horizontal_res*.5)*(horizontal_fov/horizontal_res)
                y_ang = (y_avg - vertical_res*.5)*(vertical_fov/vertical_res)


                print("X CENTER PIXEL: "+str(x_avg)+" Y CENTER PIXEL: "+str(y_avg))
                print("MARKER POSITION: x="+x+" y= "+y+" z="+z)
        except Exception as e:
            print('Target likely not found. Error: '+str(e))

        cv2.imshow('Frame', im)  # Display the frame

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    im.release()  # Release the capture object
    cv2.destroyAllWindows()  # Close all OpenCV windows


if now_landing == 0:
    landing_drone()
    print("Drone is landing!!")
