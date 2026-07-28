from enum import Enum
from System.Drivetrain import*
from System.GPS import *
from timer import *
from System.Localizer import Localizer,Camera,Lidar
from System.mapping import Map
from System.interface_map import *
from System.Pathing import Pathing, Path
import asyncio



PING_TIME = 1 #Every half a second
UPDATE_TIME = 0.05

class Robot:
    on = True
    gamepad = None
    state = RobotState.RESTING
    ping_stopwatch = Stopwatch();
    update_timer = Timer()

    joy_x = 0
    joy_y = 0


    telemetry = Telemetry(
        mode="",
        x=10,
        y=0,
        heading=0,
        vector_x = Pathing.vector_x,
        vector_y = Pathing.vector_y,
        arduino_connected=False,
        gps_data="",
        paths="",
        obstacles = "",
        status="",
        camera_stream = ""
    )
    
    def set_joystick(values : str):
        if (not Robot.state == RobotState.GAMEPAD):
            return
        x,y = values.split(",")
        Robot.joy_x = float(x)
        Robot.joy_y = float(y)
    def modify_path(command : str,values : str):
        if (command == Command.ADD_PATH.value):
            x,y = values.split(",")
            x = float(x)
            y = float(y)
            Pathing.paths.append(Path(x,y,0))
            print("path added: ",x,y,0)
        elif (command == Command.DELETE_ALL_PATHS.value):
            print("paths cleared")
            Pathing.paths.clear()
        elif (command == Command.DELETE_PATH.value):
            i = int(values)
            if i >= 0 and i < len(Pathing.paths):
                print("Deleted path: ",i)
                Pathing.paths.pop(i)
        elif (command == Command.SET_PATH_YAW.value):
            i,yaw = values.split(",")
            i = int(i)
            yaw = float(yaw)
            yaw = math.radians(yaw)
            if i >= 0 and i < len(Pathing.paths):
                path = Pathing.paths[i]
                if (isinstance(path,Path)):
                    path.yaw = yaw
        elif (command == Command.SET_PATH_INDEX.value):
            i,new_index = values.split(",")
            i = int(i)
            new_index = int(new_index)
            print(i,new_index)
            if i >= 0 and i < len(Pathing.paths):
                if (not isinstance(Pathing.paths[i],Path)):
                    return
                if new_index > len(Pathing.paths) - 1:
                    new_index = len(Pathing.paths) - 1
                if new_index < 0:
                    new_index = 0
                Pathing.paths.insert(new_index,Pathing.paths.pop(i))

    def set_state(state):
        Robot.joy_x = 0
        Robot.joy_y = 0
        if (Robot.state == state):
            return
        if (state == RobotState.MAP_CONTROL):
            Localizer.target_x = Localizer.x
            Localizer.target_y = Localizer.y
        Robot.state = state
    def turn_off():
        print("Turn off Robot")
        Robot.on = False
        Robot.set_state(RobotState.RESTING)
        stop_arduino()
        Lidar.stop()
        Camera.stop()
    def initiate():
        print("initiate")
        Robot.on = True
        Robot.state = RobotState.RESTING
        Robot.ping_stopwatch.go()
        Drivetrain.initiate()
        Localizer.start()
        Arduino.connect_arduino()
    def status():
        return f"\nOn: {Robot.on}\nState: {Robot.state.value}"
    def update():
        Robot.telemetry = Telemetry(
            mode=Robot.state.value,
            x=Localizer.x,
            y=Localizer.y,
            heading=Localizer.yaw,
            vector_x = Pathing.vector_x,
            vector_y = Pathing.vector_y,
            gps_data=GPS.get_data(),
            arduino_connected=Arduino.connected,
            obstacles = Map.print_nodes(Map.nodes),
            paths=Pathing.paths_to_string(),
            status= "\n---ROBOT---\n" +  Robot.status() + Drivetrain.status() + Localizer.status(),
            camera_stream=Camera.base64_frame
        )
        Localizer.run()
        if (not Robot.on or Robot.state == RobotState.RESTING):
            Robot.joy_x = 0
            Robot.joy_y = 0
        if (not Robot.on):
            return
        if (Robot.update_timer.time_passed() < UPDATE_TIME):
            asyncio.sleep(UPDATE_TIME - Robot.update_timer.time_passed())
        Robot.update_timer.reset()
        if (Robot.ping_stopwatch.time_passed() > PING_TIME):
            ping()
            Robot.ping_stopwatch.go()
        elif (Robot.state == RobotState.AUTONOMOUS):
            pass
        elif (Robot.state == RobotState.MAP_CONTROL):
            turn,drive,status = Pathing.calculate(Localizer.x,Localizer.y,Localizer.yaw,Map.nodes)
            Robot.joy_y = drive
            Robot.joy_x = turn
            print(turn,drive,status)
        Drivetrain.run(drive = Robot.joy_y, turn = Robot.joy_x, gamepad = (Robot.state == RobotState.GAMEPAD))
