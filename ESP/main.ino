//ESP32 Client Code ------ Version 1.2.1
#include <WiFi.h>
#include <PubSubClient.h>
#include <freertos.h>
#include <stdio.h>
#include "setup.h"
#include <time.h>


#define QUEUE_SIZE 5 

//Declare WiFi and MQTT parameters
const char* ssid = "[WIFI_SSID]";
const char* password = "[WIFI_PASSWORD]";
const char* mqtt_server = "[IP_ADDR]";

//Initialize last message time, WiFi client, and MQTT client
long lastMsg = 0;
WiFiClient espClient;
PubSubClient client(espClient);

//Declare task handles
TaskHandle_t logRssiHandle = NULL;
TaskHandle_t sendRssiHandle = NULL;
QueueHandle_t rssiQueue = NULL;

//Use struct to hold RSSI values and timestamps
struct recvSignalStrength {
  volatile long timestamp;
  volatile long lastRssi;
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
    if(xQueueSend(rssiQueue, &rssiVals, portMAXDELAY)){
      //Timestamp and RSSI values sent to queue successfully
    }; 
  }
}

void sendRssi(void *pvParameters){
  //Create receiving array
  recvSignalStrength rssiVals_R[QUEUE_SIZE][2];
  for(;;){
    recvSignalStrength rssiVals;
    //Receive RSSI values and timestamps from queue
    if(xQueueReceive(rssiQueue, &rssiVals, portMAXDELAY)){
      //RSSI values and timestamps received from queue successfully
      Serial.println("Data received from queue:");
      //Print received RSSI values and timestamps to serial monitor
      for(uint8_t i = 0; i < QUEUE_SIZE; i++){
        Serial.print("Timestamp: ");
        Serial.print(rssiVals[i][0].timestamp);
        Serial.print(" | RSSI: ");
        Serial.println(rssiVals[i][1].lastRssi);
      }
    }
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
  rssiQueue = xQueueCreate(QUEUE_SIZE,sizeof(struct recvSignalStrength));

  //Create freertos tasks
  xTaskCreatePinnedToCore(logRssi, "logRssi", 1000, 1, &logRssiHandle, 1);
  xTaskCreatePinnedToCore(sendRssi, "sendRssi", 1000, 1, &sendRssiHandle, 1);


}
void loop(){
}
