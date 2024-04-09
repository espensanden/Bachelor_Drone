import cv2
import cv2.aruco as aruco
import numpy as np

import time
import os
import platform
import sys
from picamera2 import Picamera2

#Resolution
horizontal_res = 640
vertical_res = 480

#Camera initialization
cv2.startWindowThread()
picam2 = Picamera2()
picam2.preview_configuration.main.size = (horizontal_res,vertical_res)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.start()


viewVideo=False
if len(sys.argv)>1:
    viewVideo=sys.argv[1]
    if viewVideo=='0' or viewVideo=='False' or viewVideo=='false':
        viewVideo=False


#OpenCV stuff
id_to_find=0
marker_size=10 #cm

realWorldEfficiency=.7 ##Since the Iterations/second are slower when the drone is flying the effeciency will be lower when flying.

cameraMatrix = np.array([[774.5585769798772, 0.0, 619.694166336029],
                         [0.0, 772.9641015632712, 352.49790332793935],
                         [0.0, 0.0, 1.0]])
distCoeffs = np.array([-0.3653858593342419, 0.1632243853386151, -0.002671633309837953, 0.00033826189145571927,
                       -0.038171194766151724])

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters_create()

seconds=0
if viewVideo==True:
    seconds=1000000
    print("Showing video feed if X11 is enabled.")
    print("Script will run until exit.")
    print("")
    print("")
else:
    seconds=5
counter=0
counter=float(counter)

start_time=time.time()
while time.time()-start_time<seconds:
    im = picam2.capture_array()
    gray_img = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    ids=''
    corners, ids, rejected = aruco.detectMarkers(image=gray_img,dictionary=aruco_dict,parameters=parameters)
    if ids is not None:
        print("Found these IDs in the frame:")
        print(ids)
    if ids is not None and ids[0] == id_to_find:
        ret = aruco.estimatePoseSingleMarkers(corners,marker_size,cameraMatrix=cameraMatrix,distCoeffs=distCoeffs)
        rvec,tvec = ret[0][0,0,:], ret[1][0,0,:]
        x="{:.2f}".format(tvec[0])
        y="{:.2f}".format(tvec[1])
        z="{:.2f}".format(tvec[2])

        marker_position="Marker position: x="+x+" y="+y+" z="+z
        print(marker_position)
        print("")
        if viewVideo==True:
            aruco.drawDetectedMarkers(im,corners, ids)
            aruco.drawAxis(im,cameraMatrix,distCoeffs,rvec,tvec,10)
            cv2.imshow('frame',im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        print("Aruco nmbr: "+str(id_to_find)+" not found in frame.")
        print("")
    counter=float(counter+1)

if viewVideo==False:
    frequency=realWorldEfficiency*(counter/seconds)
    print("")
    print("")
    print("")
    print("Iterations per second:")
    print(frequency)
    print("")

    print("Performance:")
    if frequency>10:
        print("Performance is more than enough for great precision landing.")
    elif frequency>5:
        print("Performance likely still good enough for precision landing.")
        print("This resolution likely maximizes the detection altitude of the marker.")
    else:
        print("Performance likely not good enough for precision landing.")
        print("Check if the Pi is too hot")
    print("")
cv2.destroyAllWindows()