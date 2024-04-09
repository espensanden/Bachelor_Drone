import cv2
import numpy as np
import math
from picamera2 import Picamera2
import time



first_run = 0
start_time = 0
start_time=0
end_time=0


found_count=0
notfound_count=0



id_to_find = 0
aruco_marker_size = 10 #in cm

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

#Camera FOV
horizontal_fov = 62.2 * (math.pi / 180 )
vertical_fov = 48.8 * (math.pi / 180)

vehicle_land = True


def landing_drone():
    #while True:
    global first_run, notfound_count, found_count, aruco_marker_size, start_time
    if first_run==0:
        print("First run of lander!!")
        first_run=1
        start_time=time.time()
    im = picam2.capture_array()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    ids = ''
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    
    try:
        if ids is not None and ids[0] == id_to_find:
            ret  = cv2.aruco.estimatePoseSingleMarkers(corners, aruco_marker_size, cameraMatrix, distCoeffs)
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


            

            print("x centre pixel: "+str(x_avg)+" y centre pixel: "+str(y_avg))
            print("Marker position: x="+x+" y= "+y+" z="+z)
            found_count=found_count+1
            print("")

        else:
            notfound_count=notfound_count+1

    except Exception as e:
        print('Target likely not found. Error: '+str(e))
        notfound_count=notfound_count+1
    #cv2.imshow('Frame', im)  # Display the frame

    #if cv2.waitKey(1) & 0xFF == ord('q'):
        #break

    #im.release()  # Release the capture object
    #cv2.destroyAllWindows()  # Close all OpenCV windows




if now_landing == 0:
    while vehicle_land == True:
        landing_drone()
    end_time=time.time()
    total_time=end_time-start_time
    total_time=abs(int(total_time))
    print("Drone is landing!!")
    if found_count > 100:
        vehicle_land = False

    total_count=found_count+notfound_count
    freq_lander=total_count/total_time
    print("Total iterations: "+str(total_count))
    print("Total seconds: "+str(total_time))
    print("------------------")
    print("lander function had frequency of: "+str(freq_lander))
    print("------------------")
    print("Vehicle has landed")
    print("------------------")