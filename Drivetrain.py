from Hardware import*
import math
from HardwareMap import Device
class Drivetrain:
    left_motor = None
    right_motor = None
    CHANGE_THRESHOLD = 0.05
    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft)
        Drivetrain.right_motor = Motor(Device.DriveRight)
        Drivetrain.drive = 0
        Drivetrain.turn = 0
    def stop():
        Drivetrain.left_motor.stop()
        Drivetrain.right_motor.stop()
    def run(drive,turn):
        #Too small or no change means dont waste bits sending redundant data
        drive_difference = abs(drive - Drivetrain.drive)
        turn_difference = abs(turn - Drivetrain.turn)
        
        if (drive_difference + turn_difference < Drivetrain.CHANGE_THRESHOLD):
            print("Srop")
            return
        Drivetrain.drive = drive
        Drivetrain.turn = turn

        scale = abs(drive) + abs(turn)
        drive = drive * scale
        turn = turn * scale
        if drive == 0 and turn == 0:
            Drivetrain.left_motor.stop()
            Drivetrain.right_motor.stop()
            return
        #Denominator to maintain ratio at extreme values
       # denominator = max(abs(drive) + abs(turn),1)
        print("Left:", drive + turn)
        print("Right: ", drive - turn)
        Drivetrain.left_motor.set((drive + turn))
        Drivetrain.right_motor.set((drive - turn))