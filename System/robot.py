from enum import Enum
from System.subsystems import*
from System.controller import *
from System.timer import *
from pydantic import BaseModel


class RobotState(Enum):
    RESTING = "RESTING"
    GAMEPAD = "GAMEPAD"
    AUTONOMOUS = "AUTONOMOUS"
class TelemetryDataTypes(BaseModel):
    mode: str
    battery: float
    longitude: float
    heading: float
    status: str

class ClientInputDataTypes(BaseModel):
    command: str
    joy_x: float
    joy_y: float

def command_to_robot(command: str):
    print(f"command: {command}")
    Robot.set_state(command)

PING_TIME = 0.5 #Every half a second
UPDATE_TIME = 0.05

class Robot:
    on = True
    gamepad = None
    state = RobotState.RESTING
    ping_stopwatch = Stopwatch();
    update_timer = Timer()

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
        time.sleep(0.5)
    def update():
        if (not Robot.on):
            return
        if (Robot.update_timer.time_passed() < UPDATE_TIME):
            time.sleep(UPDATE_TIME - Robot.update_timer.time_passed())
        Robot.update_timer.reset()
        if (Robot.ping_stopwatch.time_passed() > PING_TIME):
            ping()
            Robot.ping_stopwatch.go()
        if (Robot.state == RobotState.GAMEPAD and Robot.gamepad.is_connected()):
            Drivetrain.run(Robot.gamepad.LeftJoystickY,Robot.gamepad.RightJoystickX)
            if (Robot.gamepad.b_was_pressed()):
                Robot.turn_off()