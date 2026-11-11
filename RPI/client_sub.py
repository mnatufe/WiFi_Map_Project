import paho.mqtt.client as mqtt
import time
import threading

TIMEOUT = 10
rssiVal = 0.0
#store time on prog star
last_message_time = time.time()
def calculate_rssi_distance(rssi):
    for i in range(len(rssi)):
        if rssi[i] == '-':
            rssi = float(rssi[i:i+4])  # Convert the substring starting from '-' to float
            break
    # Constants for the path loss model
    tx_power = -62.5  # RSSI value at 1 meter (in dBm)
    n = 2.8         # Path loss exponent (environmental factor (indoor))

    # Calculate distance using the path loss formula
    distance = 10 ** ((tx_power - rssi) / (10 * n))
    return distance

def on_connect(client, userdata, flags, rc):
   global flag_connected
   flag_connected = 1
   client_subscriptions(client)
   print("Connected to MQTT server")

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected from MQTT server")
   
# a callback functions 
def callback_esp32_sensor1(client, userdata, msg):
    rssiVal  = msg.payload.decode('utf-8')
    print('ESP sensor data: ', rssiVal)
    calculated_distance = calculate_rssi_distance(rssiVal)
    print(f"Calculated distance from RSSI: {calculated_distance:.2f} meters")

def callback_esp32_sensor2(client, userdata, msg):
    rssiVal2  = msg.payload.decode('utf-8')
    print('ESP sensor data2: ', rssiVal)
    calculated_distance2 = calculate_rssi_distance(rssiVal2)
    print(f"Calculated distance from RSSI: {calculated_distance2:.2f} meters")

def callback_esp32_sensor3(client, userdata, msg):
    rssiVal3  = msg.payload.decode('utf-8')
    print('ESP sensor data3: ', rssiVal3)
    calculated_distance3 = calculate_rssi_distance(rssiVal3)
    print(f"Calculated distance from RSSI: {calculated_distance3:.2f} meters")


def callback_esp32_sensor2(client, userdata, msg):
    print('ESP sensor2 data: ', str(msg.payload.decode('utf-8')))

def callback_rpi_broadcast(client, userdata, msg):
    print('RPi Broadcast message:  ', str(msg.payload.decode('utf-8')))
    global last_message_time 
    last_message_time = time.time()

def client_subscriptions(client):
    client.subscribe("esp32/+/rssi")
"""def check_timeout():
    while True:
        #Calculate time since last
      elapsed_time = time.time()-last_message_time
      #print(elapsed_time)
      if elapsed_time > TIMEOUT:
        print("WARNING: No MQTT message received for 10 seconds")
      time.sleep(1) 
"""

# client = mqtt.Client("rpi_client1") #this should be a unique name
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, 'rpi_client1')
flag_connected = 0

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.message_callback_add('esp32/+/rssi', callback_esp32_sensor1)
client.message_callback_add('esp32/+/rssi', callback_esp32_sensor2)
client.message_callback_add('esp32/+/rssi', callback_esp32_sensor3)
client.message_callback_add('rpi/broadcast', callback_rpi_broadcast)
client.connect('10.42.0.1',1883)
# start a new thread
client.loop_start()
#threading.Thread(target=check_timeout, daemon=True).start()
client_subscriptions(client)
print("......client setup complete............")


while True:
    time.sleep(4)
    if (flag_connected != 1):
        print("trying to connect MQTT server..")

