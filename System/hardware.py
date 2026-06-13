import time
import serial
import json
from System.hardware_map import *

from enum import Enum

PORT = "COM5"
BAUD_RATE = 9600


def send_command(command):
    print("Command: ",command)
    encoded_command = (command + "\n").encode('utf-8')
    

    print("Encoded Command: ",encoded_command)

    arduino.write(encoded_command)
    
arduino = serial.Serial(port=PORT, baudrate=BAUD_RATE, timeout=2)

def close_arduino():
    arduino.close()
def stop_arduino():
    send_command(Device.Stop,"0","0")
def ping():
    send_command(Device.Ping,"0","0")

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
    target = 0
    MINIMUM_DIFFERENCE = 0.05
    MINIMUM_POWER = 0.1
    def __init__(self,id):
        self.id = id
        self.target = 0
    def set(self,target):
        if abs(target) < Motor.MINIMUM_POWER:
            target = 0
            Motor.stop()
            return
        if abs(target - self.target) < Motor.MINIMUM_DIFFERENCE:
            return
        self.target = target

        MOTOR_RANGE = 255
        target = target * MOTOR_RANGE
        target = int(target)
        if (target > MOTOR_RANGE):
            target = MOTOR_RANGE
        send_command(f'{self.id},{Request.SET.value},{target}')
    def stop(self):
        self.target = 0
        send_command(f'{self.id},{Request.OFF.value},{None}')
