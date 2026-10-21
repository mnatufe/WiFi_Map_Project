//Include all setup here, makes code easier to read
//Setup ------ Version 1.2.0

#ifndef SETUP_H
#define SETUP_H

void setup_wifi();
void connect_mqttServer();
void callback(char* topic, byte* message, unsigned int length);
void getCurrentTime(void);

#endif SETUP_H
