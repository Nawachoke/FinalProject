#include <ArduinoJson.h>

const int BUFFER_SIZE = 256; // Adjust based on the expected package size

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming data into a buffer
    char buffer[BUFFER_SIZE];
    int bytesRead = Serial.readBytesUntil('\n', buffer, BUFFER_SIZE);
    buffer[bytesRead] = '\0'; // Null-terminate the string

    // Parse the JSON package
    StaticJsonDocument<BUFFER_SIZE> doc;
    DeserializationError error = deserializeJson(doc, buffer);

    // Check for parsing errors
    if (error) {
      Serial.print("Error parsing JSON: ");
      Serial.println(error.c_str());
    } else {
      // Check for the presence of different command types
      if (doc["command"] == "position") {
        // Extract values for position command
        int x = doc["data"]["x"];
        int y = doc["data"]["y"];
        int time_value = doc["data"]["t"];

        // Process the received values
        moveRobot(x, y, time_value);
        // delay(time_value);
      } else if (doc["command"] == "stop") {
        // Process the stop command
        stopRobot();
      } else if (doc["command"] == "pause") {
        // Process the pause command
        pauseRobot();
      }
    }
  }
}

void moveRobot(int x, int y, int t) {
  // Serial.print("Robot is moving to ");
  // Serial.print(x);
  // Serial.print(" , ");
  // Serial.println(y);
  // moveDown();
  // imerse(t);
  // moveUp();
  // ShakeRack();
  // Request a new point from python
  Serial.println("request");
}

void stopRobot() {
  // Implement your robot stop logic here
  Serial.println("Robot stopped");
}

void pauseRobot() {
  // Implement your robot pause logic here
  Serial.println("Paused");
}

void imerse(int time_value){
  // Implement your imersing task
  Serial.println("imersing");
  delay(time_value * 100);
}

void moveUp(){
  // write your z- movement here
  Serial.println("moving up");
}

void moveDown(){
  // write your z+ movement here
  Serial.println("moving down");
}

void ShakeRack(){
  // Implement shaking method to spilt chemical from the rack
  Serial.println("Shaking the rack!");
}