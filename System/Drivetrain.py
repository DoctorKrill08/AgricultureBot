import math

import numpy as np

from System.Constants import *
from System.hardware import *
from timer import Timer


class Drivetrain:

    left_motor : Motor
    right_motor : Motor
    telemetry = ""


    MAX_POWER = 0.3
    MIN_TURN = 0.05

    TURN_P = -0.38
    DRIVE_P = 0.015

    timer = Timer()
    @staticmethod
    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
        Drivetrain.timer.reset()
    @staticmethod
    def status():
        telemetry = "\n--- DRIVETRAIN ---\n"
        telemetry += Drivetrain.left_motor.status()
        telemetry += Drivetrain.right_motor.status()
        telemetry += f'\nDRIVE_P: {Drivetrain.DRIVE_P}\nTURN_P: {Drivetrain.TURN_P}'
        return telemetry
    @staticmethod
    def to_scale(drive : float,turn : float,gamepad = True):
        if (abs(drive) + abs(turn) < Drivetrain.MAX_POWER):
            return drive,turn
        sum = abs(drive) + abs(turn)
        scale = Drivetrain.MAX_POWER/sum
        return (drive * scale),(turn * scale)
    @staticmethod
    def stop():
        Drivetrain.left_motor.stop()
        Drivetrain.right_motor.stop()
    @staticmethod
    def run(drive : float,turn : float,gamepad = True):
        drive = -drive
        drive,turn = Drivetrain.to_scale(drive,turn,gamepad)
        Drivetrain.left_motor.set(drive + turn)
        Drivetrain.right_motor.set(drive - turn)

        Drivetrain.timer.reset()
    @staticmethod
    def calculate_turn(delta_yaw : float):
        return Drivetrain.TURN_P * delta_yaw
    @staticmethod
    def vector_to_drive(vector_x,vector_y,yaw):
        distance = math.sqrt((vector_x ** 2) + (vector_y  ** 2))
        target_yaw = math.atan2(vector_y,vector_x)
        delta_yaw = shortest_angular_distance(yaw,target_yaw)
        target_turn = Drivetrain.calculate_turn(delta_yaw)
        target_drive = Drivetrain.DRIVE_P * distance * math.cos(delta_yaw)
        if (target_drive < 0):
            target_drive = 0
        if (abs(target_turn) > 0.8):
            target_turn = 0.8 * (target_turn / abs(target_turn))
        if (abs(target_turn) > 0.5):
            target_drive = 0
        if (target_drive > 0.5):
            target_drive = 0.5
        return target_turn,target_drive
