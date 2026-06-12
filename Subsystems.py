from Hardware import*
import math
from HardwareMap import Device



class Drivetrain:
    left_motor = None
    right_motor = None
    CHANGE_THRESHOLD = 0.05
    telemetry = ""
    def initiate():
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
        #Too small or no change means dont waste bits sending redundant data
        drive_difference = abs(drive - Drivetrain.drive)
        turn_difference = abs(turn - Drivetrain.turn)
        
        if (drive_difference + turn_difference < Drivetrain.CHANGE_THRESHOLD):
            return
        Drivetrain.drive = drive
        Drivetrain.turn = turn

        drive,turn = Drivetrain.to_scale(drive,turn)
        if drive == 0 and turn == 0:
            Drivetrain.left_motor.stop()
            Drivetrain.right_motor.stop()
            return
        #Denominator to maintain ratio at extreme values
       # denominator = max(abs(drive) + abs(turn),1)
        print("Left:", drive + turn)
        print("Right: ", drive - turn)
        Drivetrain.telemetry = f"Left: {drive + turn}"
        Drivetrain.left_motor.set((drive + turn))
        Drivetrain.right_motor.set((drive - turn))