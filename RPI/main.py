#----------Version 1.1.0-------------
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
import paho.mqtt.client as mqtt
from mpu6050 import mpu6050

#Set sensor address
sensor = mpu6050(0x68)




#Read data from the IMU in a loop
try:
    while True:
        # Read accelerometer data (returns a dict with x, y, z in m/s²)
        accel_data = sensor.get_accel_data()
        
        # Read gyroscope data (returns a dict with x, y, z in deg/s)
        gyro_data = sensor.get_gyro_data()

        
        # Format and display output streams
        print(f"Accel (m/s²) -> X: {accel_data['x']:6.2f} | Y: {accel_data['y']:6.2f} | Z: {accel_data['z']:6.2f}")
        print(f"Gyro  (deg/s) -> X: {gyro_data['x']:6.2f} | Y: {gyro_data['y']:6.2f} | Z: {gyro_data['z']:6.2f}")
        print("-" * 55)
        
        # Poll every 100ms
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")




#Send signal and receive timestamped ESP32 RSSI

#Import point cloud file, process and add inference placement, output new image
