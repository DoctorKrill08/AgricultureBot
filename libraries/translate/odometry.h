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

const double TICKS_PER_ROTATION = 35391; //35391
const double WHEEL_DIAMETER = 7.67717;
const double WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * PI;
const double DISTANCE_BETWEEN_WHEELS = 11.267717;

double ticksToInches(long ticks){
    return ((ticks / TICKS_PER_ROTATION) * WHEEL_CIRCUMFERENCE);
}
void calculateOdometry(long right, long left){
    prevRight = rightPos;
    prevLeft = leftPos;

    rightPos = right;
    leftPos = left;

    deltaLeft = (double)((leftPos - prevLeft));
    deltaRight = (double)((rightPos - prevRight));

    leftInches = ticksToInches(deltaLeft);
    rightInches = ticksToInches(deltaRight);

    averageDisplacement = (rightInches + leftInches) / 2.000;

    deltaYaw = (double)((rightInches - leftInches) / DISTANCE_BETWEEN_WHEELS);
    
    x += averageDisplacement * cos((yaw + (deltaYaw / 2.0000)));
    y += averageDisplacement * sin((yaw) + (deltaYaw / 2.0000));

    yaw += deltaYaw;
}
#endif