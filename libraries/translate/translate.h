// AUTOMATICALLY GENERATED FILE - DO NOT EDIT DIRECTLY

// Input char value of device, ex. DriveLeft = '1', output type, ex. 'M' -> Motor
#ifndef COMMANDS_H
#define COMMANDS_H

char getType(char key){
    switch(key){

        case '1':
         return 'M';

        case '2':
         return 'M';

        case '3':
         return 'B';

        case '4':
         return 'M';

        case '5':
         return 'M';

        case '6':
         return 'M';

        case '7':
         return 'M';

        case '8':
         return 'S';

        case '9':
         return 'S';

        case '10':
         return 'S';

        case '11':
         return 'S';
   };
}
#endif;
const char SERVO_VALUE = 'S';
const char MOTOR_VALUE = 'M';
const char BATTERY_VALUE = 'B';
struct Request {
    int OFF = 0;
    int SET = 1;
    int GET = 2;
};
struct Device {
    int DriveLeft = 1;
    int DriveRight = 2;
    int Battery = 3;
    int Turret = 4;
    int ShoulderLeft = 5;
    int ShoulderRight = 6;
    int Elbow = 7;
    int Wrist = 8;
    int ClawRot = 9;
    int Claw = 10;
    int Blade = 11;
};