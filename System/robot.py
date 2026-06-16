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
    arduino_connected: bool
    gamepad_connected: bool
    status: str

class ClientInputDataTypes(BaseModel):
    command: str
    joy_x: float
    joy_y: float

PING_TIME = 0.5 #Every half a second
UPDATE_TIME = 0.05



class Robot:
    on = True
    gamepad = None
    state = RobotState.RESTING
    ping_stopwatch = Stopwatch();
    update_timer = Timer()

    telemetry = TelemetryDataTypes(
        mode=state.value,
        battery=12.4,
        longitude=10,
        latitude=0,
        heading=0,
        arduino_connected=False,
        gamepad_connected=False,
        status="",
    )
    

    def set_state(state):
        if (Robot.state == state):
            return
        if (state == RobotState.GAMEPAD):
            Robot.gamepad,connected = check_gamepad(Robot.gamepad)
            if (not connected):
                return
        Robot.state = state
    def turn_off():
        print("Turn off Robot")
        Robot.on = False
        Robot.set_state(RobotState.RESTING)
        stop_arduino()
        close_arduino()
    def turn_on():
        print("Turn on Robot")
        Robot.initiate()
        Robot.on = True
    def initiate():
        print("initiate")
        Robot.state = RobotState.RESTING
        Arduino.connect_arduino()
        time.sleep(0.25)
        Drivetrain.initiate()
        time.sleep(0.25)
        Robot.gamepad,_ = create_gamepad()
    def update():
        Robot.telemetry = TelemetryDataTypes(
            mode=Robot.state.value,
            battery=12.4,
            longitude=10,
            latitude=0,
            heading=0,
            gamepad_connected=gamepad_connected(Robot.gamepad),
            arduino_connected=Arduino.connceted,
            status=Drivetrain.status(),
        )
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
