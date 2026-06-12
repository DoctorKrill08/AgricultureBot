#include <Arduino.h>
#include <Servo.h>

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

String SERVO_STRING_VALUE = "S";
String MOTOR_STRING_VALUE = "M";


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
  if (request == 0){
    servo.detach();
    return 0;
  }else if (request == 1){
    servo.write(value);
  }else if (request == 2){
    return servo.read();
  }
  return -1;
}
int motorCommand(int driverPort, int pwmPort,  int request, int value){
  //Turn off
  if (request == 0){
    digitalWrite(driverPort, LOW);
    analogWrite(pwmPort, 0);
    return 0;
  }
  //set target
  if (request == 1){
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
const int servoPort = 5;
Servo testServo;

const int LeftDriveMotorDriverPort = 12;
const int LeftDriveMotorPWMPort = 4;

const int RightDriveMotorDriverPort = 10;
const int RightDriveMotorPWMPort = 2;

String idToString(int id){
  if (id == 0){
    return "S";
  }
  if (id == 1 or id == 2){
    return "M";
  }
  return;
}


Servo idToServo(int id){
  if (id == 0){
    return testServo;
  }
  return;
}

Motor idToMotor(int id){
  //Returns driver port and pwm port
  if (id == 1){
    Motor motor;
    motor.driverPort = LeftDriveMotorDriverPort;
    motor.pwmPort = LeftDriveMotorPWMPort;
    return motor;
  }else if (id == 2){
    Motor motor;
    motor.driverPort = RightDriveMotorDriverPort;
    motor.pwmPort = RightDriveMotorPWMPort;
    return motor;
  }
  return;
}


void setup() {
  // put your setup code here, to run once:
 // int result = myFunction(2, 3);
  Serial.begin(BAUD_RATE); 
  testServo.attach(servoPort);
  pinMode(LeftDriveMotorDriverPort, OUTPUT);
  pinMode(LeftDriveMotorPWMPort, OUTPUT);
  pinMode(RightDriveMotorDriverPort, OUTPUT);
  pinMode(RightDriveMotorPWMPort, OUTPUT);

}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming byte
    String message = Serial.readStringUntil('\n');

    Command cmd = parseCommand(message.c_str());

    String type = idToString(cmd.id);
    if (type == SERVO_STRING_VALUE){
      Servo servo = idToServo(cmd.id);
      int result = servoCommand(servo,cmd.request,cmd.value);
    }else if (type == MOTOR_STRING_VALUE){
      Motor motor = idToMotor(cmd.id);
      int result = motorCommand(motor.driverPort,motor.pwmPort,cmd.request,cmd.value);
    }
  }
}
