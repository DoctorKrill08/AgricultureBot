from System.hardware import*
from timer import Timer
import math

def configurable_variables(cls,vars):
    configurables = {}
    for i in range(len(vars)):
        configurables[i] = vars[i].__name__
    cls.configurables = configurables
def set_config_var(cls,var_name,value):
    if (not isinstance(value,float)):
        return
    try:
        cls.__dict__.get(var_name) = value
        print("Successful config ",var_name, " = ", value)
    except:
        print("Failed to config ", var_name)

class Drivetrain:

    left_motor = None
    right_motor = None
    telemetry = ""


    MAX_POWER = 0.75
    TURN_SENSITIVITY = 0.5
    MIN_TURN = 0.1
    FORWARD_SPEED = 0.1 #TBD
    TURN_SPEED = 0.1

    configurable_variables([MAX_POWER,TURN_SENSITIVITY,MIN_TURN,FORWARD_SPEED,TURN_SPEED])
    
    x = 0
    y = 0
    yaw = 0

    timer = Timer()

    def initiate():
        Drivetrain.left_motor = Motor(Device.DriveLeft.value)
        Drivetrain.right_motor = Motor(Device.DriveRight.value)
        Drivetrain.timer.reset()
    def status():
        telemetry = "--- DRIVETRAIN ---\n"
        telemetry += Drivetrain.left_motor.status()
        telemetry += Drivetrain.right_motor.status()
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

        Drivetrain.state_estimate(drive,turn,Drivetrain.timer.time_passed())
        Drivetrain.timer.reset()
    def state_estimate(drive,turn,deltaT):
        Drivetrain.yaw += (turn * deltaT) * Drivetrain.TURN_SPEED
        Drivetrain.x += ((drive * deltaT) * Drivetrain.TURN_SPEED) * math.cos(Drivetrain.yaw)
        Drivetrain.y += ((drive * deltaT) * Drivetrain.TURN_SPEED) * math.sin(Drivetrain.yaw)
