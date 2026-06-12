import time
import serial
import json
from HardwareMap import *

from enum import Enum

PORT = "COM5"
BAUD_RATE = 9600


def send_command(command):
    print("Command: ",command)
    encoded_command = (command + "\n").encode('utf-8')

    print("Encoded Command: ",encoded_command)

    arduino.write(encoded_command)
    
arduino = serial.Serial(port=PORT, baudrate=BAUD_RATE, timeout=1)

def close_arduino():
    arduino.close()


class Servo:
    TYPE = HardwareType.SERVO
    def __init__(self,id):
        self.id = id
    def set(self,target):
        send_command(f'{self.id},{Request.SET.value},{target}')
    def get(self):
        send_command(f'{self.id},{Request.GET.value},{None}')
    def turn_off(self):
        send_command(f'{self.id},{Request.OFF.value},{None}')
class Motor:
    TYPE = HardwareType.MOTOR
    def __init__(self,id):
        self.id = id
    def set(self,target):
        MOTOR_RANGE = 255
        target = target * MOTOR_RANGE
        target = int(target)
        if (target > MOTOR_RANGE):
            target = MOTOR_RANGE
        send_command(f'{self.id},{Request.SET.value},{target}')
    def stop(self):
        send_command(f'{self.id},{Request.OFF.value},{None}')
