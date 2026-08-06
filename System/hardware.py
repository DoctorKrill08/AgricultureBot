import time
from enum import Enum

import serial

from System.hardware_map import *


class Arduino:
    SERIAL_PORT = '/dev/arduino_device'
    TIMEOUT = 0.1
    serial = None
    connected = False
    @staticmethod
    def connect_arduino():
        Arduino.connected = False
        try:
            Arduino.serial = serial.Serial(Arduino.SERIAL_PORT, 115200, timeout= Arduino.TIMEOUT)
            Arduino.connected = True
            print(f"Arduino connected: {Arduino.connected}")
        except:
            Arduino.connected = False
        time.sleep(1.5)
        if (Arduino.connected):
            Arduino.send_command(f"{Device.Ping.value},0",override=True)
    @staticmethod
    def send_command(command,read = False,override = False):
        if (not Arduino.connected and not override):
            return
        encoded_command = (command + "\n").encode('utf-8')
        try:
            Arduino.serial.write(encoded_command)

            if read:
                raw_data = Arduino.serial.readline()
                decoded = raw_data.decode('utf-8').strip()
                return decoded
        except:
            Arduino.connected = False
            print("Arduino disconnected")
    @staticmethod
    def close():
        if (not Arduino.connected):
            return
        Arduino.serial.close()
        Arduino.connected = False
    @staticmethod
    def stop():
        cmd = Arduino.send_command(f"{Device.Stop.value},0",read=True,override=True)
        if (cmd != None and cmd != ""):
            Arduino.close()
    @staticmethod
    def ping():
        Arduino.send_command(f"{Device.Ping.value},0",read=True)
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
        Arduino.send_command(f'{self.id},{target}')
    def stop(self):
        self.target = 0
        Arduino.send_command(f'{self.id},{"0"}')
