import time
import serial
import json
from System.hardware_map import *

from enum import Enum




class Arduino:
    NANO = "NANO"
    WINDOWS = "WINDOWS"
    SERIAL_PORTS = {
        NANO: '/dev/arduino_device',
        WINDOWS : 'COM5'
    }
    TIMEOUT = 0.1
    serial = None
    connected = False
    def connect_arduino():
        Arduino.connected = False
        for key,value in Arduino.SERIAL_PORTS.items():
            if (Arduino.connected):
                return
            try:
                Arduino.serial = serial.Serial(value, 115200, timeout= Arduino.TIMEOUT)
                print(f"Connected to Arduino via {key}: {value}")
                Arduino.connected = True
                print(f"Arduino connected: {Arduino.connected}")
            except:
                Arduino.connected = False
        time.sleep(1.5)
        if (Arduino.connected):
            send_command(f"{Device.Ping.value},0",override=True)
def send_command(command,read = False,override = False):
    if (not Arduino.connected and not override):
        print("Arduino not connected")
        return
    print("Command: ",command)
    encoded_command = (command + "\n").encode('utf-8')

    Arduino.serial.write(encoded_command)

    if read:
        raw_data = Arduino.serial.readline()
        decoded = raw_data.decode('utf-8').strip()
        print(decoded)
        return decoded

def close_arduino():
    Arduino.serial.close()
    Arduino.connected = False
def stop_arduino():
    cmd = send_command(f"{Device.Stop.value},0",read=True,override=True)
    if (not cmd == None and not cmd == ""):
        close_arduino()
def ping():
    send_command(f"{Device.Ping.value},0",read=True)
class Motor:
    TYPE = HardwareType.MOTOR
    target = 0
    MINIMUM_DIFFERENCE = 0.02
    MINIMUM_POWER = 0.05
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
        send_command(f'{self.id},{target}')
    def stop(self):
        self.target = 0
        send_command(f'{self.id},{"0"}')
