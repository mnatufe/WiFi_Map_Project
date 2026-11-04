#----------Version 1.2.0-------------
#IMU daq through MPU6050, Dist measurement through ToF
#Enable I2C interface on Raspberry Pi prior to running
# sudo raspi-config
# Interfacing Options >> I2C >> Yes
# sudo reboot
#verify broadcasting with "i2cdetect -y 1" command, should see "UU" on address 0x68 for MPU6050 IMU

#Install required libraries:
#sudo apt update
#sudo apt install python3-smbus python3-dev i2c-tools

#Install MPU6050 library:
#sudo pip3 install mpu6050-raspberrypi --break-system-packages
#Remove the --break-system-packages flag if using virtual environment

#Pinout:
#MOSI - GPIO 10 (Pin 19)
#MISO - GPIO 9 (Pin 21)
#SCLK - GPIO 11 (Pin 23)
#CS - GPIO 8 (Pin 24)


import time
import board
import busio
import adafruit_vl53l0x
import csv
import paho.mqtt.client as mqtt
from mpu6050 import mpu6050


#Set IMU sensor address
sensor = mpu6050(0x68)

# Initialize I2C bus and sensor.
i2c = busio.I2C(board.SCL, board.SDA)
vl53 = adafruit_vl53l0x.VL53L0X(i2c)

#Timing budget for distance measurement
vl53.measurement_timing_budget = 100000 #100ms, same timing as RSSI measurement

#Read data from the IMU in a loop
try:
    while True:
        # Read accelerometer data (returns a dict with x, y, z in m/s²)
        accel_data = sensor.get_accel_data()
        
        # Read gyroscope data (returns a dict with x, y, z in deg/s)
        gyro_data = sensor.get_gyro_data()

        #Store X & Z data
        x_accel = accel_data['x']
        z_accel = accel_data['z']
        x_gyro = gyro_data['x']
        z_gyro = gyro_data['z']
        
        # Format and display output streams
        print(f"Accel (m/s²) -> X: {x_accel:6.2f} | Z: {z_accel:6.2f}") #2D only, Y axis not used
        print(f"Gyro  (deg/s) -> X: {x_gyro:6.2f} | Z: {z_gyro:6.2f}")
        print("-" * 55)


        #print range every 100ms on every read
        distance = vl53.range
        print(f"Distance: {distance} mm")

        print("-" * 55)
        print(time.time())
        time.sleep(0.1)


except KeyboardInterrupt:
    print("Exiting...")




#Send signal and receive timestamped ESP32 RSSI

#Import point cloud file, process and add inference placement, output new image
