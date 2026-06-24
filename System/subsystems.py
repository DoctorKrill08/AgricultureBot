from System.hardware import*
import math



class Drivetrain:
    left_motor = None
    right_motor = None
    telemetry = ""
    MAX_POWER = 0.75
    TURN_SENSITIVITY = 0.5
    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
    def status():
        telemetry = "--- DRIVETRAIN ---\n"
        telemetry += Drivetrain.left_motor.status()
        telemetry += Drivetrain.right_motor.status()
        return telemetry
    def to_scale(drive,turn):
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
