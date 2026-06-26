from enum import Enum
from System.subsystems import*
from System.controller import *
from System.timer import *
from System.Camera import Camera
from System.interface_map import RobotState
from pydantic import BaseModel


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

PING_TIME = 1 #Every half a second
UPDATE_TIME = 0.05


class Auto():
    timer = None
    RUN_TIME = 10
    def __init__(self):
        self.timer = Timer()
    def loop(self):
        pass
    def end(self):
        Robot.set_state(RobotState.RESTING)
class DriveForwardWithCamera(Auto):
    def __init__(self):
        self.timer = Timer()
    def loop(self):
        Robot.joy_x = 0
        Robot.joy_y = 0.35
        if (Camera.to_close or not Camera.on):
            Robot.joy_x = 0
            Robot.joy_y = 0
        if (self.timer.time_passed() > self.RUN_TIME):
            self.end()
    def end(self):
        Robot.set_state(RobotState.RESTING)
class PIDIMU(Auto):
    def __init__(self):
        self.timer = Timer()
        Camera.reset_imu()
    def loop(self):
        Robot.joy_x = 0
        Robot.joy_y = 0
        kP = 0.001
        if (Camera.on):
            error = Camera.yaw()
            Robot.joy_x = kP * error
        if (self.timer.time_passed() > self.RUN_TIME):
            self.end()
    def end(self):
        Robot.set_state(RobotState.RESTING)


class Robot:
    on = True
    gamepad = None
    state = RobotState.RESTING
    ping_stopwatch = Stopwatch();
    update_timer = Timer()

    joy_x = 0
    joy_y = 0

    auto = Auto()

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
    
    def set_joystick(values : str):
        if (not Robot.state == RobotState.GAMEPAD):
            return
        x,y = values.split(",")
        Robot.joy_x = float(x)
        Robot.joy_y = float(y)
    def set_state(state):
        if (Robot.state == state):
            return
        if (state == RobotState.GAMEPAD):
            Robot.gamepad,connected = check_gamepad(Robot.gamepad)
        if (state == RobotState.AUTONOMOUS):
            Robot.auto = DriveForwardWithCamera()
        Robot.state = state
    def turn_off():
        print("Turn off Robot")
        Robot.on = False
        Robot.set_state(RobotState.RESTING)
        stop_arduino()
        close_arduino()
        Camera.stop()
    def turn_on():
        print("Turn on Robot")
        Robot.initiate()
        Robot.on = True
    def initiate():
        print("initiate")
        Robot.state = RobotState.RESTING
        Arduino.connect_arduino()
        Robot.ping_stopwatch.go()
        Drivetrain.initiate()
        Camera.start()
    def update():
        Robot.telemetry = TelemetryDataTypes(
            mode=Robot.state.value,
            battery=12.4,
            longitude=10,
            latitude=0,
            heading=0,
            gamepad_connected=gamepad_connected(Robot.gamepad),
            arduino_connected=Arduino.connected,
            status=Drivetrain.status(),
        )
        Camera.read()
        if (not Robot.on or Robot.state == RobotState.RESTING):
            Robot.joy_x = 0
            Robot.joy_y = 0
        if (not Robot.on):
            return
        if (Robot.update_timer.time_passed() < UPDATE_TIME):
            time.sleep(UPDATE_TIME - Robot.update_timer.time_passed())
        Robot.update_timer.reset()
        if (Robot.ping_stopwatch.time_passed() > PING_TIME):
            ping()
            Robot.ping_stopwatch.go()
        if (Robot.state == RobotState.GAMEPAD):
            if (Robot.gamepad.is_connected()):
                Robot.joy_y = Robot.gamepad.LeftJoystickY
                Robot.joy_x = Robot.gamepad.RightJoystickX
            if (Robot.gamepad.b_was_pressed()):
                Robot.turn_off()
        elif (Robot.state == RobotState.AUTONOMOUS):
            Robot.auto.loop()
        Drivetrain.run(drive = Robot.joy_y, turn = Robot.joy_x)
