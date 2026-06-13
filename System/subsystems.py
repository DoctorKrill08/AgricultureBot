from System.hardware import*
import math



class Drivetrain:
    left_motor = None
    right_motor = None
    CHANGE_THRESHOLD = 0.05
    MINIMUM_POWER = 0.1
    telemetry = ""
    def __init__(self):
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
        Drivetrain.drive = 0
        Drivetrain.turn = 0
    def to_scale(drive,turn):
        if (abs(drive) + abs(turn) < 1):
            return drive,turn
        sum = abs(drive) + abs(turn)
        scale = 1/sum
        return (drive * scale),(turn * scale)
    def stop():
        Drivetrain.left_motor.stop()
        Drivetrain.right_motor.stop()
    def run(drive,turn):
        drive,turn = Drivetrain.to_scale(drive,turn)
        #Denominator to maintain ratio at extreme values
       # denominator = max(abs(drive) + abs(turn),1)
        print("Left:", drive + turn)
        print("Right: ", drive - turn)
        Drivetrain.telemetry = f"Left: {drive + turn}"
        Drivetrain.left_motor.set((drive + turn))
        Drivetrain.right_motor.set((drive - turn))