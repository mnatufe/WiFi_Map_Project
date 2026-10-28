//ESP32 Client Code ------ Version 2.2.0
#include <WiFi.h>
#include <PubSubClient.h>
#include <stdio.h>
#include "setup.h"
#include <time.h>
#include <Arduino.h>


#define QUEUE_SIZE 5
#define DEVICE_ID "ESP32_1" 

//Declare WiFi and MQTT parameters
const char* ssid = "RPI_456";
const char* password = "";
const char* mqtt_server = "10.42.0.1";

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
  long timestamp;
  long lastRssi;
};

//Logs and sends timestamped RSSI values to queue
void logRssi(void *pvParameters){
  recvSignalStrength rssiVals;

  for(;;){

    rssiVals.lastRssi = WiFi.RSSI(); //Log RSSI value (dBm)
    rssiVals.timestamp = getCurrentTime(); //Get current time since epoch (seconds)
    xQueueSend(rssiQueue, &rssiVals, portMAX_DELAY); //Send RSSI values and timestamps to queue

    vTaskDelay(100 / portTICK_PERIOD_MS); //Delay for 100 milliseconds
  }
}

void sendRssi(void *pvParameters){
  recvSignalStrength rssiVals_R;
  //Create receiving array
  recvSignalStrength rssiBatch[QUEUE_SIZE];
  for(;;){      
    for(uint8_t i = 0; i < QUEUE_SIZE; i++){
      //Receive RSSI values and timestamps from queue
      if(xQueueReceive(rssiQueue, &rssiVals_R, portMAX_DELAY)){
        rssiBatch[i] = rssiVals_R;
        //RSSI values and timestamps received from queue successfully
        Serial.println("Data received from queue:");
      }
    }
    
    //Convert RSSI values and timestamps to string format for MQTT publishing
    String rssiMsg = "";
    for(uint8_t i = 0; i < QUEUE_SIZE; i++){
      rssiMsg += String(DEVICE_ID) + "Timestamp: " + String(rssiBatch[i].timestamp) + ", RSSI: " + String(rssiBatch[i].lastRssi) + "\n";
    }
    //Append device ID to MQTT topic for publishing
    char mqttTopic[100];
    snprintf(mqttTopic, sizeof(mqttTopic), "esp32/%s/rssi", DEVICE_ID);

    //Pass through MQTT to RPI 
    if (!client.connected()) {
      connect_mqttServer();
    }

    client.loop();

    long now = millis();
    if (now - lastMsg > 4000) {
      lastMsg = now;
      client.publish(mqttTopic, rssiMsg);
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
