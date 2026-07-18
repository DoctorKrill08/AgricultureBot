#ifndef ODOMETRY_H
#define ODOMETRY_H

#include "Arduino.h"

long rightPos = 0;
long leftPos = 0;

long prevRight = 0;
long prevLeft = 0;

double deltaRight = 0;
double deltaLeft = 0;

double rightInches = 0;
double leftInches = 0;
double wheelDifference = 0; //used for displacement
double averageDisplacement = 0;
double deltaYaw = 0;

double  yaw = 0;
double x = 0;
double  y = 0;

const double TICKS_PER_ROTATION = 35391;
const double WHEEL_DIAMETER = 7.5;
const double WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * PI;
const double DISTANCE_BETWEEN_WHEELS = 12.00;

double ticksToInches(long ticks){
    return ((ticks / TICKS_PER_ROTATION) * WHEEL_CIRCUMFERENCE);
}
void odometryClear(){
    deltaYaw = 0;
    x = 0;
    y = 0;
}
void calculateOdometry(int right, int left){
    if (prevRight == right and prevLeft == left){
        return
    }

    prevRight = rightPos;
    prevLeft = leftPos;

    rightPos = right;
    leftPos = left;

    deltaLeft = (double)((leftPos - prevLeft));
    deltaRight = (double)((rightPos - prevRight));

    leftInches = ticksToInches(deltaLeft);
    rightInches = ticksToInches(deltaRight);

    wheelDifference = (double)(rightInches - leftInches); 

    averageDisplacement = (rightInches + leftInches) / 2.000;

    deltaYaw = (double)(wheelDifference / DISTANCE_BETWEEN_WHEELS);
    
    x += averageDisplacement * cos(yaw + (deltaYaw / 2));
    y += averageDisplacement * sin(yaw + (deltaYaw / 2));

    yaw += deltaYaw;

    while (yaw > PI){
        yaw -= 2 * PI;
    }
    while (yaw < -PI){
        yaw += 2 * PI;
    }
}
#endif
