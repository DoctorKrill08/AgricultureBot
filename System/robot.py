from enum import Enum
from System.subsystems import*
from System.controller import *
from System.timer import *
from pydantic import BaseModel


class RobotState(Enum):
    RESTING = "RESTING"
    GAMEPAD = "GAMEPAD"
    AUTONOMOUS = "AUTONOMOUS"
    OFF = "OFF"
class TelemetryDataTypes(BaseModel):
    mode: str
    battery: float
    longitude: float
    latitude: float
    heading: float
    status: str
    fps: float
    ping: float

class ClientInputDataTypes(BaseModel):
    command: str
    joy_x: float
    joy_y: float

def command_to_robot(command: str):
    print(f"command: {command}")
    if (command == RobotState.OFF.value):
        Robot.turn_off()
        return
    Robot.set_state(RobotState[command])

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
        close_arduino()
    def initiate():
        print("initiate")
        Arduino.connect_arduino()
        time.sleep(0.5)
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



telemetry = TelemetryDataTypes(
    mode=Robot.state.value,
    battery=12.4,
    longitude=-79.791,
    latitude=36.072,
    heading=45.2,
    status="Driving",
    fps=0,
    ping=0
)