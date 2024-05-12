import cv2
import numpy as np
import math
from picamera2 import Picamera2
import time
from dronekit import connect, VehicleMode,LocationGlobal,LocationGlobalRelative
from pymavlink import mavutil


#Variables
takeoff_height = 3.2 #meter
velocity = 0.5

first_run = 0
start_time = 0
start_time=0
end_time=0


found_count=0
notfound_count=0

targetAltitude = 3.2

id_to_find = 0
aruco_marker_size = 10 #in cm

script_mode = 1
ready_to_land = 0

#Distortion Coefficients
cameraMatrix = np.array([[774.5585769798772, 0.0, 619.694166336029],
                         [0.0, 772.9641015632712, 352.49790332793935],
                         [0.0, 0.0, 1.0]])
distCoeffs = np.array([-0.3653858593342419, 0.1632243853386151, -0.002671633309837953, 0.00033826189145571927,
                       -0.038171194766151724])

aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters_create()

#Camera configuration
horizontal_res = 640
vertical_res = 480
picam2 = Picamera2()
picam2.preview_configuration.main.size = (horizontal_res,vertical_res)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

#Camera FOV for Pi cam v2
horizontal_fov = 62.2 * (math.pi / 180 )
vertical_fov = 48.8 * (math.pi / 180)


manualArm = False






def arm_and_takeoff(targetHeight):
        while vehicle.is_armable!=True:
                print("Waiting for vehicle to become armable.")
                time.sleep(1)
        print("Vehicle is now armable")
        
        vehicle.mode = VehicleMode("GUIDED")
                
        while vehicle.mode!='GUIDED':
                print("Waiting for drone to enter GUIDED flight mode")
                time.sleep(1)
        print("Vehicle now in GUIDED MODE. Have fun!!")

        if manualArm==False:
            vehicle.armed = True
            while vehicle.armed==False:
                print("Waiting for vehicle to become armed.")
                time.sleep(1)
        else:
            if vehicle.armed == False:
                print("Exiting script. manualArm set to True but vehicle not armed.")
                print("Set manualArm to True if desiring script to arm the drone.")
                return None
        print("Look out! Props are spinning!!")
                
        vehicle.simple_takeoff(targetHeight) ##meters

        while True:
                print("Current Altitude: %d"%vehicle.location.global_relative_frame.alt)
                if vehicle.location.global_relative_frame.alt>=.95*targetHeight:
                        break
                time.sleep(1)
        print("Target altitude reached!!")

        return None


def send_local_ned_velocity(vx, vy, vz):
	msg = vehicle.message_factory.set_position_target_local_ned_encode(
		0,
		0, 0,
		mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
		0b0000111111000111,
		0, 0, 0,
		vx, vy, vz,
		0, 0, 0,
		0, 0)
	vehicle.send_mavlink(msg)
	vehicle.flush()
    
def send_land_message(x,y):
    msg = vehicle.message_factory.landing_target_encode(
        0,
        0,
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
        x,
        y,
        0,
        0,
        0,)
    vehicle.send_mavlink(msg)
    vehicle.flush()



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
    if vehicle.mode!='LAND':
        vehicle.mode=VehicleMode("LAND")
        while vehicle.mode!='LAND':
            print('WAITING FOR DRONE TO ENTER LAND MODE')
            time.sleep(1)

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

            if vehicle.mode!='LAND':
                vehicle.mode = VehicleMode('LAND')
                while vehicle.mode!='LAND':
                    time.sleep(1)
                print("------------------------")
                print("Vehicle now in LAND mode")
                print("------------------------")
                send_land_message(x_ang,y_ang)
            else:
                send_land_message(x_ang,y_ang)
                print("Vehicle is now in land mode 2 else")
                pass

            print("x centre pixel: "+str(x_avg)+" y centre pixel: "+str(y_avg))
            print("Marker position: x = "+x+" y = "+y+" z = "+z)
            found_count=found_count+1
            print("")

        else:
            notfound_count=notfound_count+1

    except Exception as e:
        print('Target likely not found. Error: '+str(e))
        notfound_count=notfound_count+1

#    cv2.imshow('Frame', im)  # Display the frame


#Vehicle connect
vehicle = connect('/dev/ttyAMA0',baud=57600,wait_ready=True)

##SETUP PARAMETERS TO ENABLE PRECISION LANDING
vehicle.parameters['PLND_ENABLED'] = 1
vehicle.parameters['PLND_TYPE'] = 1 ##1 for companion computer
vehicle.parameters['PLND_EST_TYPE'] = 0 ##0 for raw sensor, 1 for kalman filter pos estimation
vehicle.parameters['LAND_SPEED'] = 20 ##Descent speed of 30cm/s

print(vehicle.parameters['PLND_ENABLED'])
print(vehicle.parameters['PLND_TYPE'])

if script_mode == 1:
    arm_and_takeoff(takeoff_height)
    print(str(time.time()))
    time.sleep(1)
    ready_to_land = 1

if ready_to_land == 1:
    while vehicle.armed == True:
        landing_drone()
    end_time=time.time()
    total_time=end_time-start_time
    total_time=abs(int(total_time))
    print("Drone is landing!!")

    total_count=found_count+notfound_count
    freq_lander=total_count/total_time
    print("Total iterations: "+str(total_count))
    print("Total seconds: "+str(total_time))
    print("*******************")
    print("Landing_drone function had frequency of: "+str(freq_lander))
    print("*******************")
    print("Vehicle has landed")
    print("*******************")