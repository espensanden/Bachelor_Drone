from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time

import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='127.0.0.1:14550')
args = parser.parse_args()

connection_string = args.connect

vehicle = connect(connection_string, wait_ready=True)

def arm_and_takeoff(aTarget_altitude):
    print("Basic pre-arm checks")

    while not vehicle.is_armable:
        print("Waiting for vehicle to connect")
        time.sleep()

    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming..")
        time.sleep(1)
    
    print("Taking off!")
    vehicle.simple_takeoff(aTarget_altitude)

    #Checking if the vehicle has reached takeoff altitude
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        #Set a ca goal altitude
        if vehicle.location.global_relative_frame.alt>=aTarget_altitude*0.95:
            print("Reached target altitude.")
            break
        time.sleep(1)

#Start sequence to arm and take off
arm_and_takeoff(10)

print("Takeoff complete")

#Hover for 10 seconds
time.sleep(10)

print("Now lets land")

vehicle.mode = VehicleMode("LAND")

#Close the vehicle object
vehicle.close()







