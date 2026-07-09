#ifndef ODOMETRY_H
#define ODOMETRY_H

#include "Arduino.h"

int rightPos = 0;
int leftPos = 0;

int prevRight = 0;
int prevLeft = 0;

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
const double DISTANCE_BETWEEN_WHEELS = 13.00;

double ticksToInches(int ticks){
    return ((ticks / TICKS_PER_ROTATION) * WHEEL_CIRCUMFERENCE);
}

void calculateOdometry(int right, int left){
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
    
    x += averageDisplacement * cos(yaw);
    y += averageDisplacement * sin(yaw);

    deltaYaw = (double)(wheelDifference / DISTANCE_BETWEEN_WHEELS);

    yaw += deltaYaw;

    if (yaw > PI){
        yaw -= 2 * PI;
    }
    if (yaw < -PI){
        yaw += 2 * PI;
    }
}
#endif
