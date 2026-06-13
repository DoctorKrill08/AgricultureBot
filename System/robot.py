from enum import Enum
from System.subsystems import*
from System.controller import *

class RobotState(Enum):
    RESTING = "RESTING"
    GAMEPAD = "GAMEPAD"
    AUTONOMOUS = "AUTONOMOUS"

class Robot:
    on = True
    gamepad = None
    state = RobotState.RESTING
    def set_state(state):
        if (Robot.state == state):
            return
        if (state == RobotState.GAMEPAD):
            Robot.gamepad,connected = check_gamepad(Robot.gamepad)
            if (not connected):
                return
        Robot.state = state
    def turn_off():
        Robot.on = False
        stop_arduino()
        arduino.close()
    def initiate():
        Drivetrain.initiate()
    def update():
        if (not Robot.on):
            return
        ping()
        if (Robot.state == RobotState.GAMEPAD and Robot.gamepad.is_connected()):
            Drivetrain.run(Robot.gamepad.LeftJoystickY,Robot.gamepad.RightJoystickX)
            if (Robot.gamepad.b_was_pressed()):
                Robot.turn_off()