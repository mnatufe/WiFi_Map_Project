//ESP32 Client Code ------ Version 2.0.1
#include <WiFi.h>
#include <PubSubClient.h>
#include <freertos.h>
#include <stdio.h>
#include "setup.h"
#include <time.h>


#define QUEUE_SIZE 5
#define DEVICE_ID "ESP32_1" 

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
  long timestamp;
  long lastRssi;
};

//Logs and sends timestamped RSSI values to queue
void logRssi(void *pvParameters){
  recvSignalStrength rssiVals;

  for(;;){

    lastRssi = WiFi.RSSI(); //Log RSSI value (dBm)
    timestamp = getCurrentTime(); //Get current time since epoch (seconds)
    xQueueSend(rssiQueue, &rssiVals, portMAX_DELAY); //Send RSSI values and timestamps to queue

    vTaskDelay(100 / portTICK_PERIOD_MS); //Delay for 100 milliseconds
  }
}

void sendRssi(void *pvParameters){
  recvSignalStrength rssiVals_R;
  //Create receiving array
  recvSignalStrength rssiBatch[QUEUE_SIZE];
  for(;;){
    
    
      
    //Print received RSSI values and timestamps to serial monitor
    for(uint8_t i = 0; i < QUEUE_SIZE; i++){
      //Receive RSSI values and timestamps from queue
      if(xQueueReceive(rssiQueue, &rssiVals_R, portMAX_DELAY)){
        rssiBatch[i] = rssiVals_R;
        //RSSI values and timestamps received from queue successfully
        Serial.println("Data received from queue:");
      }
    }
    //finish later gts
    
    //Convert RSSI values and timestamps to string format for MQTT publishing
    char convertedVals [QUEUE_SIZE][2][20];
    for(uint8_t i = 0; i < QUEUE_SIZE; i++){
      snprintf(convertedVals[i][0], sizeof(convertedVals[i][0]), "%ld", rssiVals_R[i][0].timestamp);
      snprintf(convertedVals[i][1], sizeof(convertedVals[i][1]), "%ld", rssiVals_R[i][1].lastRssi);
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
      client.publish(mqttTopic, convertedVals[i][1]);
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
