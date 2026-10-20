//ESP32 Client Code ------ Version 1.0.0
#include <WiFi.h>
#include <PubSubClient.h>
#include <freertos.h>
#include <stdio.h>

const char* ssid = "[WIFI_SSID]";
const char* password = "";
const char* mqtt_server = "[IP_ADDR]";

WiFiClient espClient;
PubSubClient client(espClient);


//Setup freertos tasks
//create RSSI timestamped multidimensional array
//Pass through MQTT to RPI (Append device ID)
