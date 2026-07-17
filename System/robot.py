from enum import Enum
from System.subsystems import*
from System.GPS import *
from timer import *
from System.Localizer import Localizer,Camera
from System.mapping import Map
from System.interface_map import *
from System.Pathing import Pathing



PING_TIME = 1 #Every half a second
UPDATE_TIME = 0.05

class AutoState(Enum):
    CRUISE = "CRUISE"
    AIM = "AIM"
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
        if (Camera.obstructed or not Camera.on):
            Robot.joy_x = 0
            Robot.joy_y = 0
        if (self.timer.time_passed() > self.RUN_TIME):
            self.end()
    def end(self):
        Robot.set_state(RobotState.RESTING)
class ObstacleAvoidAuto(Auto):
    def __init__(self):
        self.timer = Timer()
    def loop(self):
        Robot.joy_x = 0
        Robot.joy_y = 0.35
        if (not Camera.on):
            Robot.joy_x = 0
            Robot.joy_y = 0
        else:
            Robot.joy_x = Camera.turn
            Robot.joy_y = Robot.joy_y + Camera.drive
            if (Robot.joy_y < 0):
                Robot.joy_y = 0
            if (Robot.joy_y > 0.5):
                Robot.joy_y = 0.5
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

    auto_state = AutoState.AIM
    auto = Auto()

    telemetry = Telemetry(
        mode=state.value,
        battery=12.4,
        x=10,
        y=0,
        tx = 0,
        ty = 0,
        target_yaw=0,
        heading=0,
        arduino_connected=False,
        gps_connected=False,
        map = "",
        status="",
    )
    
    def set_joystick(values : str):
        if (not Robot.state == RobotState.GAMEPAD):
            return
        x,y = values.split(",")
        Robot.joy_x = float(x)
        Robot.joy_y = float(y)
    def set_position(values : str):
        if (not Robot.state == RobotState.MAP_CONTROL):
            return
        x,y = values.split(",")
        Localizer.target_x = float(x)
        Localizer.target_y= float(y)
        print(x,y)
    def set_state(state):
        if (Robot.state == state):
            return
        if (state == RobotState.AUTONOMOUS):
            Robot.auto = ObstacleAvoidAuto()
        Robot.state = state
    def turn_off():
        print("Turn off Robot")
        Robot.on = False
        Robot.set_state(RobotState.RESTING)
        stop_arduino()
        Camera.stop()
    def initiate():
        print("initiate")
        Robot.state = RobotState.RESTING
        Robot.ping_stopwatch.go()
        Drivetrain.initiate()
        Localizer.start()
        #GPS.connect_gps()
        Arduino.connect_arduino()
        Robot.on = True
    def status():
        return f"Auto Time: {Robot.auto.RUN_TIME} \n"
    def update():
        Robot.telemetry = Telemetry(
            mode=Robot.state.value,
            battery=12.4,
            x=Localizer.x,
            y=Localizer.y,
            heading=Localizer.yaw,
            tx=Localizer.target_x,
            ty = Localizer.target_y,
            target_yaw=Localizer.target_yaw,
            gps_connected=GPS.rover.connected,
            arduino_connected=Arduino.connected,
            map = Map.print_nodes(Map.nodes),
            status= "\n---ROBOT---\n" +  Robot.status() + Drivetrain.status() + Localizer.status(),
        )
        Localizer.run()
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
        elif (Robot.state == RobotState.AUTONOMOUS):
            Robot.auto.loop()
        elif (Robot.state == RobotState.MAP_CONTROL):
            turn,drive,status = Pathing.calculate(Localizer.x,Localizer.y,Localizer.yaw,Localizer.target_x,Localizer.target_y,Map.nodes)
            Robot.joy_y = drive
            Robot.joy_x = turn
            print(turn,drive,status)
            if (Camera.obstructed):
                Robot.joy_y = 0
                Robot.joy_x = 0
        Drivetrain.run(drive = Robot.joy_y, turn = Robot.joy_x, gamepad = (Robot.state == RobotState.GAMEPAD))
