//Include all setup here, makes code easier to read
//Setup ------ Version 1.3.0

#ifndef SETUP_H
#define SETUP_H


extern const char* ssid;
extern const char* password;
extern PubSubClient client;

void setup_wifi();
void connect_mqttServer();
void callback(char* topic, byte* message, unsigned int length);
time_t getCurrentTime();

#endif
