import time
import serial
import json
from System.hardware_map import *

from enum import Enum

PORT = "COM5"
BAUD_RATE = 9600


class Arduino:
    serial = None
    connceted = False
    def connect_arduino():
        try:
            Arduino.serial = serial.Serial(port=PORT, baudrate=BAUD_RATE, timeout=2)
            Arduino.connceted = True
        except:
            Arduino.connceted = False
        print(f"Arduino connected: {Arduino.connceted}")

def send_command(command):
    if (not Arduino.connceted):
        print("Arduino not connected")
        return
    print("Command: ",command)
    encoded_command = (command + "\n").encode('utf-8')
    

    print("Encoded Command: ",encoded_command)

    Arduino.serial.write(encoded_command)
    raw_data = Arduino.serial.readline()
    print(raw_data.decode('utf-8').strip())

def close_arduino():
    if (Arduino.connceted == False):
        return
    Arduino.serial.close()
    Arduino.connceted = False
def stop_arduino():
    send_command(f"{Device.Stop.value},0,0")
def ping():
    print("Ping")
    send_command(f"{Device.Ping.value},0,0")
class Servo:
    TYPE = HardwareType.SERVO
    id = None
    initiated = False
    target = 0
    def __init__(self,id):
        self.id = id
        self.initiated = True
    def set(self,target):
        self.target = target
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
    id = None
    initiated = False
    def __init__(self,id):
        self.id = id
        self.target = 0
        self.initiated = True
    def status(self):
        if (self.id == None):
            return ""
        return f" {Device(self.id).name} POWER: {self.target} "
    def set(self,target):
        if abs(target) < Motor.MINIMUM_POWER:
            if (self.target == 0):
                return
            target = 0
            self.stop()
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
