import cv2
import numpy as np
import math
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

cameraMatrix = np.array([[774.5585769798772, 0.0, 619.694166336029],
                         [0.0, 772.9641015632712, 352.49790332793935],
                         [0.0, 0.0, 1.0]])
distCoeffs = np.array([-0.3653858593342419, 0.1632243853386151, -0.002671633309837953, 0.00033826189145571927,
                       -0.038171194766151724])

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters_create()

horizontal_res = 640
vertical_res = 480

horizontal_fov = 62.2 * (math.pi / 180 )  # Pi cam V2: 62.2
vertical_fov = 48.8 * (math.pi / 180)     # Pi cam V2: 48.8


while True:
    im = picam2.capture_array()

    #if not ret:
        #print("Failed to capture frame")
        #break

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(im, corners, ids)

        for i in range(len(ids)):
            ret = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.1, cameraMatrix, distCoeffs)
            (rvec, tvec) = (ret[0][0, 0, :], ret[1][0, 0, :])

            x = '{:.2f}'.format(tvec[0])
            y = '{:.2f}'.format(tvec[1])
            z = '{:.2f}'.format(tvec[2])

            x_sum = np.sum(corners[i][0][:, 0])
            y_sum = np.sum(corners[i][0][:, 1])

            x_avg = x_sum * 0.25
            y_avg = y_sum * 0.25

            x_ang = (x_avg - horizontal_res * 0.5) * (horizontal_fov / horizontal_res)
            y_ang = (y_avg - vertical_res * 0.5) * (vertical_fov / vertical_res)

            print("Marker ID:", ids[i], "Position: x =", x, "y =", y, "z =", z)
            print("Center Pixel: x =", x_avg, "y =", y_avg)

    cv2.imshow('Frame', im)  # Display the frame

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

im.release()  # Release the capture object
cv2.destroyAllWindows()  # Close all OpenCV windows
