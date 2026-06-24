#ifndef LED_H
#define LED_H

#include "Arduino.h"
const long BLINK_TIME = 300;
long ledBlinkStartTime = millis();
bool ledBlinking = false;
bool ledOn = false;

const int LED_PORT = 7;

void ledUpdate(){
    unsigned long blink_elapsed_time = millis() - ledBlinkStartTime;
    if (ledBlinking == false){
        return;
    }
    if (blink_elapsed_time > BLINK_TIME){
        ledOn = !ledOn;
        ledBlinkStartTime = millis();
        if (ledOn == false){
            digitalWrite(LED_PORT,LOW);
        }else{
            digitalWrite(LED_PORT,HIGH); //ON
        }
    }
}
void ledBlink(){
    ledBlinking = true;
    ledBlinkStartTime = millis();
}
void ledStayOn(){
    ledBlinking = false;
    digitalWrite(LED_PORT,HIGH);
    ledOn = true;
}
#endif
