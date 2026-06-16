#include <Arduino.h>
#include <Servo.h>

#include <translate.h>

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

    sscanf(input, "%d,%d,%d",
           &cmd.id,
           &cmd.request,
           &cmd.value);

    return cmd;
}

int servoCommand(Servo servo, int request, int value){
  if (request == OFF){
    servo.detach();
    return 0;
  }else if (request == SET){
    servo.write(value);
  }else if (request == GET){
    return servo.read();
  }
  return -1;
}
int motorCommand(int driverPort, int pwmPort,  int request, int value){
  //Turn off
  if (request == OFF){
    digitalWrite(driverPort, LOW);
    analogWrite(pwmPort, 0);
    return 0;
  }
  //set target
  if (request == SET){
    if (value < 0){
      digitalWrite(driverPort, LOW);
      value = value * -1;
    }else{
      digitalWrite(driverPort, HIGH);
    }
    analogWrite(pwmPort, value);
    return 0;
  }
  return -1;
}

int BAUD_RATE = 9600;
const int clawPort = 5;

const int DriveLeftMotorDriverPort = 12;
const int DriveLeftMotorPWMPort = 4;

const int DriveRightMotorDriverPort = 10;
const int DriveRightMotorPWMPort = 2;

Servo clawServo;

Motor driveLeftMotor = {DriveLeftMotorDriverPort,DriveLeftMotorPWMPort};
Motor driveRightMotor = {DriveRightMotorDriverPort,DriveRightMotorPWMPort};


Servo getServo(int id){
  if (id == Claw){
    return clawServo;
  }
  return;
}

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
    int result = motorCommand(driveLeftMotor.driverPort,driveLeftMotor.pwmPort,OFF,0);
    result = motorCommand(driveRightMotor.driverPort,driveRightMotor.pwmPort,OFF,0);
}

//IF THE ARDUINO STOPS RECEIVING SIGNALS FOR TOO LONG, ARDUINO STOPS EVERYTHING
unsigned long startTime; // Stores the starting time

void setup() {
  Serial.begin(BAUD_RATE); 
  clawServo.attach(clawPort); 
  pinMode(DriveLeftMotorDriverPort, OUTPUT);
  pinMode(DriveLeftMotorPWMPort, OUTPUT);
  pinMode(DriveRightMotorDriverPort, OUTPUT);
  pinMode(DriveRightMotorPWMPort, OUTPUT);
  startTime = millis(); 
}

const long ELAPSED_TIME_SINCE_SIGNAL_THRESHOLD_MILLIS = 1500;
bool stopped = false;

void loop() {
  unsigned long elapsedTime = millis() - startTime; 
  if (elapsedTime > ELAPSED_TIME_SINCE_SIGNAL_THRESHOLD_MILLIS){
    stop();
  }
  if (Serial.available() > 0) {
    // Read the incoming byte
    String message = Serial.readStringUntil('\n');

    Command cmd = parseCommand(message.c_str());


    if (cmd.id >= 0){
      startTime = millis();
    }
    if (cmd.id == Ping){
      return;
    }
    if (cmd.id == Stop){
      stopped = true;
      stop();
      return;
    }
    if (stopped == true){
      stop();
      return;
    }


    char type = getType(cmd.id);
    if (type == SERVO_VALUE){
      Servo servo = getServo(cmd.id);
      int result = servoCommand(servo,cmd.request,cmd.value);
    }else if (type == MOTOR_VALUE){
      Motor motor = getMotor(cmd.id);
      int result = motorCommand(motor.driverPort,motor.pwmPort,cmd.request,cmd.value);
    }
  }
}
