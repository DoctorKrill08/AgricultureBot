#ifndef ODOMETRY_H
#define ODOMETRY_H

#include "Arduino.h"

int rightPos = 0;
int leftPos = 0;

int prevRight = 0;
int prevLeft = 0;

int deltaRight = 0;
int deltaLeft = 0;

float rightVelocity = 0; //Inches per second
float leftVelocity = 0;

float averageVelocity = 0; //used for displacement

float deltaVelocity = 0; //Used for angle change

float averageDisplacement = 0;
float deltaYaw = 0;

float yaw = 0;
float x = 0;
float y = 0;

const int TICKS_PER_ROTATION = 38638;
const float WHEEL_RADIUS = 3.625;
const double WHEEL_CIRCUMFERENCE = (WHEEL_RADIUS * 2) * PI;
const float DISTANCE_BETWEEN_WHEELS = 10;
const double ROBOT_CIRCUMFERENCE = DISTANCE_BETWEEN_WHEELS * PI;

float ticksToInches(float ticks){
    return ((ticks / TICKS_PER_ROTATION) * WHEEL_CIRCUMFERENCE);
}

void calculateOdometry(int right, int left, int deltaTime){
    prevRight = rightPos;
    prevLeft = leftPos;

    rightPos = right;
    leftPos = left;

    deltaLeft = leftPos - prevLeft;
    deltaRight = rightPos - prevRight;

    rightVelocity = deltaRight / deltaTime;
    leftVelocity = deltaLeft / deltaTime;

    rightVelocity = ticksToInches(rightVelocity);
    leftVelocity = ticksToInches(leftVelocity);

    averageVelocity = (rightVelocity + leftVelocity) / 2;

    deltaVelocity = rightVelocity - leftVelocity;

    averageDisplacement = (averageVelocity * deltaTime);
    
    x += averageDisplacement * sin(yaw); //East West
    y += averageDisplacement * cos(yaw); //North South

    deltaYaw = (deltaVelocity * deltaTime) / ROBOT_CIRCUMFERENCE;

    yaw += (deltaVelocity / ROBOT_CIRCUMFERENCE);
}
#endif
