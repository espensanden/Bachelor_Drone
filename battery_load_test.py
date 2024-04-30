import time
import os
import platform
import sys

from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil

#############################
targetAltitude = 3
manualArm = False
############DRONEKIT#################
vehicle = connect('/dev/ttyAMA0', baud=57600, wait_ready=True)

# Select /dev/ttyAMA0 for UART. /dev/ttyACM0 for USB

#########FUNCTIONS###########
def arm_and_takeoff(targetHeight):
    while not vehicle.is_armable:
        print("Waiting for vehicle to become armable.")
        time.sleep(1)
    print("Vehicle is now armable")

    vehicle.mode = VehicleMode("GUIDED")

    while vehicle.mode != 'GUIDED':
        print("Waiting for drone to enter GUIDED flight mode")
        time.sleep(1)
    print("Vehicle now in GUIDED MODE. Have fun!!")

    if not manualArm:
        vehicle.armed = True
        while not vehicle.armed:
            print("Waiting for vehicle to become armed.")
            time.sleep(1)
    else:
        if not vehicle.armed:
            print("Exiting script. manualArm set to True but vehicle not armed.")
            print("Set manualArm to True if desiring script to arm the drone.")
            return None
    print("Look out! Props are spinning!!")

    vehicle.simple_takeoff(targetHeight)  # meters

    while True:
        altitude = vehicle.location.global_relative_frame.alt
        print(f"Current Altitude: {altitude:.1f}")
        if altitude >= .95 * targetHeight:
            break
        time.sleep(1)
    print("Target altitude reached!!")

def monitor_battery():
    # Create a connection for receiving battery status
    last_time = time.time()

    while True:
        try:
            battery_status = vehicle.recv_match(type='BATTERY_STATUS', blocking=True)
            if battery_status:
                current_amps = battery_status.current_battery / 100.0  # Convert to amperes
                ampere_hours_per_sec = current_amps / 3600  # Convert current to ampere-hours per second (Ah/s)
                print(f"Voltage: {battery_status.voltages[0] / 1000:.2f} V")
                print(f"Current: {current_amps:.2f} A")
                print(f"Ampere-hours per second: {ampere_hours_per_sec:.10f} Ah/s")
                print(f"Remaining Capacity: {battery_status.battery_remaining}%")
        except Exception as e:
            print(f"Failed to get battery status: {e}")
        time.sleep(1)  # Delay to avoid overwhelming the output

############MAIN###############

# Run battery monitor in a separate thread or process depending on your needs
from threading import Thread
battery_thread = Thread(target=monitor_battery)
battery_thread.start()

arm_and_takeoff(targetAltitude)

print("Take off complete.")
time.sleep(3)

print("Now let's land.")
vehicle.mode = VehicleMode("LAND")

while vehicle.mode != 'LAND':
    time.sleep(1)
    print("Waiting for drone to land")

print("Drone in land mode. Exiting script.")