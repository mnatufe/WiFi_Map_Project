import paho.mqtt.client as mqtt
import time
import threading

TIMEOUT = 10
#store time on prog star
last_message_time = time.time()

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
    print('ESP sensor data: ', msg.payload.decode('utf-8'))


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

