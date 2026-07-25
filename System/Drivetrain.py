from System.hardware import*
from timer import Timer
import math
import numpy as np
from System.Constants import *

class Drivetrain:

    left_motor = None
    right_motor = None
    telemetry = ""


    MAX_POWER = 0.4
    TURN_SENSITIVITY = 0.5
    MIN_TURN = 0.1

    TURN_P = -1.3
    DRIVE_P = 0.015

    MIN_DISTANCE = 2

    timer = Timer()

    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
        Drivetrain.timer.reset()
    def status():
        telemetry = "\n--- DRIVETRAIN ---\n"
        telemetry += Drivetrain.left_motor.status()
        telemetry += Drivetrain.right_motor.status()
        telemetry += f'\nDRIVE_P: {Drivetrain.DRIVE_P}\nTURN_P: {Drivetrain.TURN_P}'
        return telemetry
    def to_scale(drive,turn,gamepad = True):
        if (abs(turn) < Drivetrain.MIN_TURN and gamepad):
            turn = 0
        elif (not turn == 0):
            turn = turn - (turn/abs(turn)) * Drivetrain.MIN_TURN
        turn = turn * Drivetrain.TURN_SENSITIVITY
        if (abs(drive) + abs(turn) < Drivetrain.MAX_POWER):
            return drive,turn
        sum = abs(drive) + abs(turn)
        scale = Drivetrain.MAX_POWER/sum
        return (drive * scale),(turn * scale)
    def stop():
        Drivetrain.left_motor.stop()
        Drivetrain.right_motor.stop()
    def run(drive,turn,gamepad = True):
        drive = -drive
        drive,turn = Drivetrain.to_scale(drive,turn,gamepad)
        Drivetrain.left_motor.set((drive + turn))
        Drivetrain.right_motor.set((drive - turn))

        Drivetrain.timer.reset()

    def calculate_turn(delta_yaw):
        return Drivetrain.TURN_P * delta_yaw
    
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
            target_drive = 0
        if (target_drive > 0.5):
            target_drive = 0.5
        return target_turn,target_drive
