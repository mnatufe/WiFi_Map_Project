//ESP32 Client Code ------ Version 1.1.0
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

WiFiClient espClient;
PubSubClient client(espClient);

//Setup freertos tasks
//Declare task handles
TaskHandle_t logRssiHandle = NULL;
TaskHandle_t sendRssiHandle = NULL;
QueueHandle_t rssiQueue = NULL;


void logRssi(void *argument){
  for(;;){
    //Log Received Signal Strength Indicator (RSSI) values in array with timestamps, pass down queue

    //Create loop to receive and log then send using below
    xQueueSend(TIMESTAMPED_RSSI_VALUE[i][j], &TIMESTAMPED_RSSI_VALUE, portMAXDELAY); //send timestamped values
  }
}

void sendRssi(void *argument){
  for(;;){
    //Create receiving array
    //Create loop to receive then store using below
    xQueueReceive(TIMESTAMPED_RSSI_VALUE[i][j], &TIMESTAMPED_RSSI_VALUE, portMAXDELAY);
    //Pull rssi log, append device ID
    //Pass through MQTT to RPI 
  }
}

void setup(){
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server,1883);
  client.setCallback(callback);

  //Create Queue
  rssiQueue = xQueueCreate(QUEUE_SIZE,sizeof(RSSI_VALUE_SIZE));

  //Create freertos tasks
  xTaskCreatePinnedToCore(logRssi, "logRssi", 1000, 1, &logRssiHandle, 1);
  xTaskCreatePinnedToCore(sendRssi, "sendRssi", 1000, 1, &sendRssiHandle, 1);


}
void loop(){
}
