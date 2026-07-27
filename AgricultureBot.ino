#include <Arduino.h>
#include <Servo.h>

#include <translate.h>
#include <led.h>
#include <odometry.h>

struct Motor{
  int driverPort;
  int pwmPort;
};

struct Command
{
    int id;
    int request;
    int value;
};


Command parseCommand(const char* input)
{
    Command cmd;

    sscanf(input, "%d,%d",
           &cmd.id,
           &cmd.value);

    return cmd;
}

void motorCommand(Motor motor, int value){
  //Turn off
  if (value == 0){
    digitalWrite(motor.driverPort, LOW);
    analogWrite(motor.pwmPort, 0);
    return;
  }
  //set target
  if (value < 0){
    digitalWrite(motor.driverPort, LOW);
    value = value * -1;
  }else{
    digitalWrite(motor.driverPort, HIGH);
  }
  analogWrite(motor.pwmPort, value);
  return;
}

const int DriveLeftMotorDriverPort = 12;
const int DriveLeftMotorPWMPort = 4;

const int DriveRightMotorDriverPort = 10;
const int DriveRightMotorPWMPort = 2;

const int DriveRightEncoderPinA = 18; // Channel A (Interrupt pin)
const int DriveRightEncoderPinB = 19; // Channel B (Direction pin)

const int DriveLeftEncoderPinA = 20;
const int DriveLeftEncoderPinB = 21;

volatile long DriveRightEncoderPos = 0; 
volatile long DriveLeftEncoderPos = 0; 

bool connected = false;


Motor driveLeftMotor = {DriveLeftMotorDriverPort,DriveLeftMotorPWMPort};
Motor driveRightMotor = {DriveRightMotorDriverPort,DriveRightMotorPWMPort};


Motor getMotor(int id){
  switch (id)
  {
  case DriveLeft:
    return driveLeftMotor;
  case DriveRight:
    return driveRightMotor;
  default:
    return {-1,-1};
  };
};

void stop(){
    motorCommand(driveLeftMotor,0);
    motorCommand(driveRightMotor,0);
}

void turnOff(){
  connected = false;
  ledBlink();
  stop();
}

void doRightEncoder() {
  if (digitalRead(DriveRightEncoderPinA) == digitalRead(DriveRightEncoderPinB)) {
    DriveRightEncoderPos--;
  } else {
    DriveRightEncoderPos++;
  }
}

void doLeftEncoder(){
  if (digitalRead(DriveLeftEncoderPinA) == digitalRead(DriveLeftEncoderPinB)) {
    DriveLeftEncoderPos++;
  } else {
    DriveLeftEncoderPos--;
  }
}

//IF THE ARDUINO STOPS RECEIVING SIGNALS FOR TOO LONG, ARDUINO STOPS EVERYTHING
unsigned long startTime; // Stores the starting time

void setup() {
  Serial.begin(115200); 
  pinMode(DriveLeftMotorDriverPort, OUTPUT);
  pinMode(DriveLeftMotorPWMPort, OUTPUT);

  pinMode(DriveRightMotorDriverPort, OUTPUT);
  pinMode(DriveRightMotorPWMPort, OUTPUT);

  pinMode(DriveRightEncoderPinA, INPUT_PULLUP);
  pinMode(DriveRightEncoderPinB, INPUT_PULLUP);
  pinMode(DriveLeftEncoderPinA, INPUT_PULLUP);
  pinMode(DriveLeftEncoderPinB, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(DriveRightEncoderPinA), doRightEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(DriveLeftEncoderPinA), doLeftEncoder, CHANGE);

  pinMode(LED_PORT,OUTPUT);
  startTime = millis(); 
  connected = false;
}


const long ELAPSED_TIME_SINCE_SIGNAL_THRESHOLD_MILLIS = 1500;

void loop() {
  long elapsedTime = millis() - startTime; 
  if (elapsedTime > ELAPSED_TIME_SINCE_SIGNAL_THRESHOLD_MILLIS && connected == true){
    stop();
  }

  long rightTicks;
  long leftTicks;

  noInterrupts();

  rightTicks = DriveRightEncoderPos;
  leftTicks = DriveLeftEncoderPos;

  interrupts();

  calculateOdometry(rightTicks, leftTicks);
  
  ledUpdate();
  if (Serial.available() > 0) {
    // Read the incoming byte
    String message = Serial.readStringUntil('\n');

    Command cmd = parseCommand(message.c_str());
    String strConnected = "NOT CONNECTED";
    if (connected){
      strConnected = "CONNECTED";
    }

    if (cmd.id >= 0){
      startTime = millis();
      if (!connected){
        deltaYaw = 0;
        x = 0;
        y = 0;
        startTime = millis() + 5000;
        ledStayOn();
        connected = true;
      }
    }
    
    if (cmd.id == Ping){
      Serial.println(strConnected + " ARDUINO PING");
      connected = true;
      return;
    }
    if (cmd.id == Stop){
      turnOff();
      return;
    }
    if (connected == false){
      stop(); 
      return;
    }
    if (cmd.id == Odometry){
      String output = "ODOMETRY,";
      output += String(x);
      output += ",";
      output += String(y);
      output += ",";
      output += String(yaw);
      Serial.println(output);
      yaw = 0;
      x = 0;
      y = 0;
      return;
    }

    char type = getType(cmd.id);
    if (type == MOTOR_VALUE){
      motorCommand(getMotor(cmd.id),cmd.value);
    }
  }
}
