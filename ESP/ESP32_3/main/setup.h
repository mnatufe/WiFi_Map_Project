//Include all setup here, makes code easier to read
//Setup ------ Version 2.0.0

#ifndef SETUP_H
#define SETUP_H


extern const char* ssid;
extern const char* password;
extern const char* mqtt_server;
extern PubSubClient client;

void sendRssi(void *pvParameters);
void logRssi(void *pvParameters);

void setup_wifi();
void connect_mqttServer();
void callback(char* topic, byte* message, unsigned int length);
int64_t getCurrentTime();

#endif
