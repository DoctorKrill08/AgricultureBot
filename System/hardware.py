import time
import serial
import json
from System.hardware_map import *

from enum import Enum




class Arduino:
    NANO = "NANO"
    WINDOWS = "WINDOWS"
    SERIAL_PORTS = {
        NANO: '/dev/ttyACM0',
        WINDOWS : 'COM5'
    }
    serial = None
    connected = False
    def connect_arduino():
        for key,value in Arduino.SERIAL_PORTS.items():
            try:
                Arduino.serial = serial.Serial(value, BAUD_RATE, timeout=1)
                print(f"Connected to Arduino via {key}: {value}")
                Arduino.connected = True
            except:
                Arduino.connected = False
        print(f"Arduino connected: {Arduino.connected}")
        time.sleep(2)
        if (Arduino.connected):
            send_command(f"{Device.Start.value},0,0")

def send_command(command):
    if (not Arduino.connected):
        print("Arduino not connected")
        return
    print("Command: ",command)
    encoded_command = (command + "\n").encode('utf-8')

    Arduino.serial.write(encoded_command)

    raw_data = Arduino.serial.readline()
    print(raw_data.decode('utf-8').strip())

def close_arduino():
    if (Arduino.connected == False):
        return
    Arduino.serial.close()
    Arduino.connected = False
def stop_arduino():
    send_command(f"{Device.Stop.value},0,0")
def ping():
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
        send_command(f'{self.id},{Request.GET.value},{"0"}')
    def turn_off(self):
        send_command(f'{self.id},{Request.OFF.value},{"0"}')
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
        send_command(f'{self.id},{Request.OFF.value},{"0"}')
