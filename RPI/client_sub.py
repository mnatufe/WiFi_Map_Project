import paho.mqtt.client as mqtt
import time
import threading
import os
import numpy as np

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

# ---------------- Trilateration (new) ----------------

# Position of each ESP32 in meters. The keys must match the middle part of
# each ESP's topic, e.g. "esp32/esp1/rssi" -> "esp1".
ANCHORS = {
    "esp1": (0.0, 0.0),
    "esp2": (5.0, 0.0),
    "esp3": (0.0, 4.0),
}
MAX_AGE = 5          # seconds; ignore distances older than this
CSV_FILE = "position.csv"

latest = {}          # esp_id -> (distance, rssi, time received)

def parse_rssi(rssi):
    # Same parsing as calculate_rssi_distance: number starting at the '-'
    for i in range(len(rssi)):
        if rssi[i] == '-':
            return float(rssi[i:i+4])
    return float(rssi)

def trilaterate(anchors, dists):
    (x1, y1), (x2, y2), (x3, y3) = anchors
    r1, r2, r3 = dists
    A = np.array([[2*(x2-x1), 2*(y2-y1)],
                  [2*(x3-x1), 2*(y3-y1)]])
    b = np.array([r1**2 - r2**2 + x2**2 - x1**2 + y2**2 - y1**2,
                  r1**2 - r3**2 + x3**2 - x1**2 + y3**2 - y1**2])
    return np.linalg.lstsq(A, b, rcond=None)[0]

def save_position(x, y, avg_rssi, rssis):
    # rssis: individual RSSI values, in the same order as ANCHORS
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a") as f:
        if write_header:
            rssi_cols = ",".join(f"rssi_{i}" for i in ANCHORS)
            f.write(f"x,y,avg_rssi,{rssi_cols},timestamp\n")
        rssi_vals = ",".join(f"{r:.1f}" for r in rssis)
        f.write(f"{x:.2f},{y:.2f},{avg_rssi:.1f},{rssi_vals},{time.time():.2f}\n")

def callback_rssi(client, userdata, msg):
    esp_id = msg.topic.split("/")[1]
    if esp_id not in ANCHORS:
        print(f"Unknown ESP '{esp_id}' on topic {msg.topic}; add it to ANCHORS")
        return

    rssi = msg.payload.decode('utf-8')
    distance = calculate_rssi_distance(rssi)
    latest[esp_id] = (distance, parse_rssi(rssi), time.time())
    print(f"{esp_id}: RSSI {rssi} -> {distance:.2f} m")

    # Only use readings that are recent enough
    now = time.time()
    fresh = {k: (d, r) for k, (d, r, t) in latest.items() if now - t < MAX_AGE}
    if len(fresh) < 3:
        return

    ids = list(ANCHORS)
    x, y = trilaterate([ANCHORS[i] for i in ids], [fresh[i][0] for i in ids])
    rssis = [fresh[i][1] for i in ids]
    avg_rssi = sum(rssis) / len(rssis)
    print(f"Position: x = {x:.2f} m, y = {y:.2f} m, avg RSSI = {avg_rssi:.1f} dBm")
    save_position(x, y, avg_rssi, rssis)

# ------------------------------------------------------

# client = mqtt.Client("rpi_client1") #this should be a unique name
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, 'rpi_client1')
flag_connected = 0

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.message_callback_add('esp32/+/rssi', callback_rssi)
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
