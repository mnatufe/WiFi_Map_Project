//Setup file -- Version 1.2.0
#include <WiFi.h>
#include <PubSubClient.h>
#include <freertos.h>
#include <stdio.h>
#include "setup.h"
#include <time.h>
#include <Arduino.h>

//Create wifi and MQTT connection
void setup_wifi() {
  delay(50);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  //Begin WiFi connection
  WiFi.begin(ssid, password);

  //Wait while wifi connects
  int c = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    c++;
    if(c > 10) {
      ESP.restart();
    }
  }

  //Verify WiFi connection
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
//MQTT
void connect_mqttServer() {
  while (!client.connected()) {
    if(WiFi.status() != WL_CONNECTED) {
      setup_wifi();
    }

    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_client5")) {
      Serial.println("connected");
      client.subscribe("rpi/broadcast");
    }
    else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" trying again in 2 seconds");
      delay(2000);
    }
  }
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
  }
  Serial.println();
}

//Get Time
time_t getCurrentTime(){
  return time(NULL);
}
