from System.hardware import*
from timer import Timer
import math

def shortest_angular_distance(angle1, angle2):
    diff = (angle2 - angle1 + math.pi) % (2*math.pi) - math.pi
    return (diff)

class Drivetrain:

    left_motor = None
    right_motor = None
    telemetry = ""


    MAX_POWER = 0.75
    TURN_SENSITIVITY = 0.5
    MIN_TURN = 0.1

    TURN_P = 1.2
    DRIVE_P = 0.001

    MIN_DISTANCE = 2

    timer = Timer()

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
        telemetry += f'\nDRIVE_P: {Drivetrain.DRIVE_P}\nTURN_P: {Drivetrain.TURN_P}\nMIN_DISTANCE: {Drivetrain.MIN_DISTANCE}\nTARGET_DRIVE: {Drivetrain.target_drive}\nTARGET_TURN: {Drivetrain.target_turn}\n DELTA_YAW: {Drivetrain.delta_yaw}'
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
    
    def calculate_drive_vectors(x,y,yaw,target_x,target_y,target_yaw):
        deltaX = target_x - x
        deltaY = target_y - y
        Drivetrain.distance = math.sqrt((deltaX ** 2) + (deltaY ** 2))
        
        if (Drivetrain.distance > Drivetrain.MIN_DISTANCE):
            target_yaw = math.atan2(deltaX,deltaY) - (math.pi/2)
            Drivetrain.delta_yaw = shortest_angular_distance(yaw,target_yaw)
            Drivetrain.target_turn = Drivetrain.TURN_P * Drivetrain.delta_yaw
            Drivetrain.target_drive = Drivetrain.DRIVE_P * Drivetrain.distance * math.cos(Drivetrain.delta_yaw)
            if (Drivetrain.target_drive < 0):
                Drivetrain.target_drive = 0
            if (abs(Drivetrain.target_turn) > 0.3):
                Drivetrain.target_turn = 0.3 * (Drivetrain.target_turn / abs(Drivetrain.target_turn))
                Drivetrain.target_drive = 0
            if (Drivetrain.target_drive > 0.3):
                Drivetrain.target_drive = 0.3
        else:
            Drivetrain.delta_yaw = shortest_angular_distance(yaw,target_yaw)
            Drivetrain.target_turn = Drivetrain.TURN_P * Drivetrain.delta_yaw
            Drivetrain.target_drive = 0
        

