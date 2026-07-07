from System.hardware import*
from timer import Timer
import math


class Drivetrain:

    left_motor = None
    right_motor = None
    telemetry = ""


    MAX_POWER = 0.75
    TURN_SENSITIVITY = 0.5
    MIN_TURN = 0.1
    
    res = ""

    timer = Timer()

    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
        Drivetrain.timer.reset()
    def status():
        telemetry = "\n--- DRIVETRAIN ---\n"
        telemetry += Drivetrain.left_motor.status()
        telemetry += Drivetrain.right_motor.status()
        telemetry += Drivetrain.res
        telemetry += "\n"
        return telemetry
    def get_raw_odo():
        results = send_command(f'{Device.Odometry},{Request.GET.value},{"0"}',read=True)
        Drivetrain.res = results
        if (Drivetrain.res == None):
            Drivetrain.res = "RES is NONE"
    def set_odo(x=None,y=None,yaw = 0):
        value = f"x:{x},y:{y},yaw:{yaw}"
        send_command(f'{Device.Odometry},{Request.SET.value},{value}')
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

        Drivetrain.get_raw_odo()

        Drivetrain.timer.reset()

        

