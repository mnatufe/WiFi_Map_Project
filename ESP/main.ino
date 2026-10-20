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

//Create wifi and MQTT connection
void setup_wifi() {
  delay(50);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int c = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    c++;
    if(c > 10) {
      ESP.restart();
    }
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
//Setup freertos tasks
//create RSSI timestamped multidimensional array
//Pass through MQTT to RPI (Append device ID)
