from System.hardware import*
from timer import Timer
import math

def sub_angle(a1,a2):
    difference = a1 - a2
    if (difference == 0):
        return difference
    if ((a1 > 0 and a2 > 0) or (a1 < 0 and a2 < 0)):
        if (difference > math.pi):
            difference -= (2 * math.pi)
        if (difference < -math.pi):
            difference += (2 * math.pi)
        return difference
    negative = a1
    flip = 1
    if (a1 > 0):
        negative = a2
    if (abs(negative) < math.pi / 2):
        if (difference > math.pi):
            difference -= (2 * math.pi)
        if (difference < -math.pi):
            difference += (2 * math.pi)
        return difference
    if (a1 < 0):
        a1 += (2 * math.pi)
    if (a2 < 0):
        a2 += (2 * math.pi)
    difference = a1 - a2
    if (difference > math.pi):
        difference -= (2 * math.pi)
    if (difference < -math.pi):
        difference += (2 * math.pi)
    return difference * flip

class Drivetrain:

    left_motor = None
    right_motor = None
    telemetry = ""


    MAX_POWER = 0.75
    TURN_SENSITIVITY = 0.5
    MIN_TURN = 0.1

    MIN_DISTANCE = 1

    timer = Timer()

    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
        Drivetrain.timer.reset()
    def status():
        telemetry = "\n--- DRIVETRAIN ---\n"
        telemetry += Drivetrain.left_motor.status()
        telemetry += Drivetrain.right_motor.status()
        telemetry += "\n"
        return telemetry
    def to_scale(drive,turn):
        if (abs(turn) < Drivetrain.MIN_TURN):
            turn = 0
        else:
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
    def run(drive,turn):
        drive = -drive
        drive,turn = Drivetrain.to_scale(drive,turn)
        Drivetrain.left_motor.set((drive + turn))
        Drivetrain.right_motor.set((drive - turn))

        Drivetrain.timer.reset()
    
    def get_drive_vectors(target_x,target_y,target_yaw):
        pass

        

