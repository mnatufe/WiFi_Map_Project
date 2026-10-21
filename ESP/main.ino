//ESP32 Client Code ------ Version 1.2.1
#include <WiFi.h>
#include <PubSubClient.h>
#include <freertos.h>
#include <stdio.h>
#include "setup.h"
#include <time.h>


#define QUEUE_SIZE 5 

const char* ssid = "[WIFI_SSID]";
const char* password = "[WIFI_PASSWORD]";
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
struct recvSignalStrength {
  long timestamp;
  long lastRssi;
};

//Logs and sends timestamped RSSI values to queue
void logRssi(void *pvParameters){
  for(;;){

    recvSignalStrength rssiVals[QUEUE_SIZE][2]; //Array to hold  RSSI values and timestamps
    lastRssi = WiFi.RSSI(); //Log RSSI value (dBm)
    timestamp = getCurrentTime(); //Get current time since epoch (seconds)
    for(uint8_t i = 0; i < QUEUE_SIZE; i++){
      if(rssiVals[i][0].timestamp == 0){ //Check for empty slot in array
        rssiVals[i][0].timestamp = timestamp;
        rssiVals[i][1].lastRssi = lastRssi;
        break;
      }
    }
    char convertedVals [QUEUE_SIZE][2][20]; //Array to hold converted RSSI values and timestamps
    snprintf(convertedVals[0][0], sizeof(convertedVals[0][0]), "%ld", lastRssi);
    //Log Received Signal Strength Indicator (RSSI) values in array with timestamps, pass down queue

    //Create loop to receive and log then send using below
    if(xQueueSend(rssiQueue, &rssiVals, portMAXDELAY)){
      //Timestamp and RSSI values sent to queue successfully
    }; 
  }
}

void sendRssi(void *pvParameters){
  for(;;){
    //Create receiving array
    //Create loop to receive then store using below
    xQueueReceive(rssiQueue, &rssiVals, portMAXDELAY);
    //Pull rssi log, append device ID
    //Pass through MQTT to RPI 
    if (!client.connected()) {
      connect_mqttServer();
    }

    client.loop();

    long now = millis();
    if (now - lastMsg > 4000) {
      lastMsg = now;
      client.publish("esp32/sensor1/rssi", rssiVals[i][j]);
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
