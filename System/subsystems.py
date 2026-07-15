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

    TURN_P = -1.5
    DRIVE_P = 0.04

    MIN_DISTANCE = 2

    timer = Timer()

    drive_vector = np.array([0,0]) #X,Y

    DRIVE_VECTOR_MULTIPLIER = 1
    MULT = 1
    angle = 0

    target_drive = 0
    target_turn = 0

    delta_yaw = 0
    distance = 0

    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
        Drivetrain.timer.reset()
    def status():
        telemetry = "\n--- DRIVETRAIN ---\n"
        telemetry += Drivetrain.left_motor.status()
        telemetry += Drivetrain.right_motor.status()
        telemetry += f'\nDRIVE_P: {Drivetrain.DRIVE_P}\nTURN_P: {Drivetrain.TURN_P}\nMIN_DISTANCE: {Drivetrain.MIN_DISTANCE}\nTARGET_DRIVE: {Drivetrain.target_drive}\nTARGET_TURN: {Drivetrain.target_turn}\nDELTA_YAW: {Drivetrain.delta_yaw}\nVECTOR:{Drivetrain.drive_vector[0]},{Drivetrain.drive_vector[1]}'
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
    
    def vector_to_drive(x,y,yaw):
        deltaX = Drivetrain.drive_vector[0]
        deltaY = Drivetrain.drive_vector[1]
        if (Drivetrain.distance > Drivetrain.MIN_DISTANCE):
            target_yaw = math.atan2(deltaY,deltaX)# - (math.pi/2)
            Drivetrain.delta_yaw = shortest_angular_distance(yaw,target_yaw)
            Drivetrain.target_turn = Drivetrain.TURN_P * Drivetrain.delta_yaw
            Drivetrain.target_drive = Drivetrain.DRIVE_P * Drivetrain.distance * math.cos(Drivetrain.delta_yaw)
            if (Drivetrain.target_drive < 0):
                Drivetrain.target_drive = 0
            if (abs(Drivetrain.target_turn) > 0.8):
                Drivetrain.target_turn = 0.8 * (Drivetrain.target_turn / abs(Drivetrain.target_turn))
                Drivetrain.target_drive = 0
            if (Drivetrain.target_drive > 0.5):
                Drivetrain.target_drive = 0.5
        else:
            Drivetrain.delta_yaw = 0
            Drivetrain.target_turn = 0
            Drivetrain.target_drive = 0

    #Robot to Goal
    def calculate_drive_vectors(x,y,target_x,target_y):
        deltaX = target_x - x
        deltaY = target_y - y
        Drivetrain.distance = math.sqrt((deltaX ** 2) + (deltaY ** 2))
        Drivetrain.MULT = Drivetrain.DRIVE_VECTOR_MULTIPLIER
        if (Drivetrain.distance < Drivetrain.DRIVE_VECTOR_MULTIPLIER):
            Drivetrain.MULT = Drivetrain.distance
        
        Drivetrain.angle = math.atan2(deltaY,deltaX)
        Drivetrain.drive_vector = np.array([Drivetrain.MULT * math.cos(Drivetrain.angle),Drivetrain.MULT * math.sin(Drivetrain.angle)])


