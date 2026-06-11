#include <Arduino.h>
#include <Servo.h>

int BAUD_RATE = 9600;
const int servoPort = 5;
Servo servo;

// put function declarations here:
int myFunction(int, int);

void setup() {
  // put your setup code here, to run once:
 // int result = myFunction(2, 3);
  Serial.begin(BAUD_RATE); 
  servo.attach(servoPort);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming byte
    char incomingByte = Serial.read(); 
    
    if (incomingByte == '1') {
      servo.write(0);
      Serial.println("LED turned ON"); // Send response back to Python
    } else if (incomingByte == '0') {
      servo.write(100);
      Serial.println("LED turned OFF"); // Send response back to Python
    }
  }
}

// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}