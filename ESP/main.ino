//ESP32 Client Code ------ Version 1.2.0
#include <WiFi.h>
#include <PubSubClient.h>
#include <freertos.h>
#include <stdio.h>
#include "setup.h"
#include <time.h>


#define QUEUE_SIZE 5 

const char* ssid = "[WIFI_SSID]";
const char* password = "";
const char* mqtt_server = "[IP_ADDR]";

long lastMsg = 0;
WiFiClient espClient;
PubSubClient client(espClient);

//Setup freertos tasks
//Declare task handles
TaskHandle_t logRssiHandle = NULL;
TaskHandle_t sendRssiHandle = NULL;
QueueHandle_t rssiQueue = NULL;

//Use struct to hold RSSI values and timestamps
struct RSSI_VALUES {
  float timestamp;
  float rssi;
};

RSSI_VALUES TIMESTAMPED_RSSI_VALUE[QUEUE_SIZE]; //Array to hold timestamped RSSI values


void logRssi(void *argument){
  for(;;){

    long lastRssi = WiFi.RSSI(); //Log RSSI value (dBm)
    //Log Received Signal Strength Indicator (RSSI) values in array with timestamps, pass down queue

    //Create loop to receive and log then send using below
    xQueueSend(rssiQueue, &TIMESTAMPED_RSSI_VALUE, portMAXDELAY); //send timestamped values
  }
}

void sendRssi(void *argument){
  for(;;){
    //Create receiving array
    //Create loop to receive then store using below
    xQueueReceive(TIMESTAMPED_RSSI_VALUE[i][j], &TIMESTAMPED_RSSI_VALUE, portMAXDELAY);
    //Pull rssi log, append device ID
    //Pass through MQTT to RPI 
    if (!client.connected()) {
      connect_mqttServer();
    }

    client.loop();

    long now = millis();
    if (now - lastMsg > 4000) {
      lastMsg = now;
      client.publish("esp32/sensor2/temperature", temp);
      client.publish("esp32/sensor2/humidity", hum);
      Serial.println("[MQTT] Published data");
    }
  }
}

void setup(){
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server,1883);
  client.setCallback(callback);

  //Create Queue
  rssiQueue = xQueueCreate(QUEUE_SIZE,sizeof(RSSI_VALUES));

  //Create freertos tasks
  xTaskCreatePinnedToCore(logRssi, "logRssi", 1000, 1, &logRssiHandle, 1);
  xTaskCreatePinnedToCore(sendRssi, "sendRssi", 1000, 1, &sendRssiHandle, 1);


}
void loop(){
}
