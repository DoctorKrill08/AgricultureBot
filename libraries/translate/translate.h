// AUTOMATICALLY GENERATED FILE - DO NOT EDIT DIRECTLY

// Input char value of device, ex. DriveLeft = '1', output type, ex. 'M' -> Motor
#ifndef TRANSLATE_H
#define TRANSLATE_H

#include "Arduino.h"

char getType(int key){
    switch(key){

        case 1:
         return 'M';

        case 2:
         return 'M';

        case 4:
         return 'M';

        case 5:
         return 'M';

        case 6:
         return 'M';

        case 7:
         return 'M';

        case 8:
         return 'S';

        case 9:
         return 'S';

        case 10:
         return 'S';

        case 11:
         return 'S';
   };
};
#endif
static const char SERVO_VALUE = 'S';
static const char MOTOR_VALUE = 'M';
static const int BAUD_RATE = 115200;
enum Device {
    Start = -2,
    Stop = -1,
    Ping = 0,
    DriveLeft = 1,
    DriveRight = 2,
    Turret = 4,
    ShoulderLeft = 5,
    ShoulderRight = 6,
    Elbow = 7,
    Wrist = 8,
    ClawRot = 9,
    Claw = 10,
    Blade = 11,
    Odometry = 12,
};