import math
from System.mapping import Node
from System.Drivetrain import Drivetrain
from System.Constants import *
from System.interface_map import MapKey
from timer import Timer
from enum import Enum

def vector_clamp(vx,vy,max):
    v = math.sqrt((vx ** 2)+ (vy ** 2))
    if (v < max):
        return vx,vy
    angle = math.atan2(vy,vx)
    vx = max * math.cos(angle)
    vy = max * math.sin(angle)
    return vx,vy

class DynamicWindow:
    MAX_DISTANCE = 20
    MIN_DISTANCE = 1.5

    VECTOR_STRENGTH = 30
    
    UPDATE_RATE = 2

    ANGLE_INCREMENT = 15 #Degrees
    ANGLE_RANGE = 180 #Degrees

    ANGLE_PENALTY = 1
    CLEARANCE_SCORE = 1
    CHANGE_PENALTY = 10
    MIN_CHANGE_PENALTY = 5


    OBSTRUCTION_PENALTY = 100000

    MIN_CLEARANCE = ROBOT_WIDTH
    MAX_CLEARANCE = 8

    obstructed = False
    current_angle = 0

    def calculate_clearance(x,y,obstacles):
        obstructed = False
        clearance = 1000000
        for id,obstacle in obstacles.items():
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < clearance):
                clearance = distance
            if (distance < DynamicWindow.MIN_CLEARANCE + 5):
                obstructed = True
            continue
        return obstructed,clearance

    def calculate_obstruction(bot_x,bot_y,target_x,target_y,obstacles):
        delta_x = target_x - bot_x
        delta_y = target_y - bot_y
        
        angle = math.atan2(delta_y,delta_x)

        check_distance = 40
        furthest = 0
        increment = DynamicWindow.MIN_CLEARANCE / 2
        i = 0
        clearance = 100000
        obstructed = False

        complete = False
        while not complete and not obstructed:
            furthest = i * increment
            i += 1
            if (furthest > check_distance):
                furthest = check_distance
            x = furthest * math.cos(angle)
            y = furthest * math.sin(angle)
            obstructed,this_clearance = DynamicWindow.calculate_clearance(x,y,obstacles)
            if (this_clearance < clearance):
                clearance = this_clearance
            if (obstructed):
                break
            if furthest == check_distance:
                complete = True
        return obstructed,clearance
    
    
    def calculate(x,y,yaw,tx,ty,obstacles):
        delta_x = tx - x
        delta_y = ty - y
        target_yaw = math.atan2(delta_y,delta_x)
        distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))

        DynamicWindow.obstructed,clearance = DynamicWindow.calculate_obstruction(x,y,tx,ty,obstacles)
        force = min(distance,DynamicWindow.VECTOR_STRENGTH)
        if (not DynamicWindow.obstructed):
            best_path_clearance =  -10000
            DynamicWindow.current_angle = 0
            goal_vector_x = force * math.cos(target_yaw)
            goal_vector_y = force * math.sin(target_yaw)
            return goal_vector_x,goal_vector_y

        goal_vector_x = 0
        goal_vector_y = 0

        greatest_score = -10000
        best_path_clearance = 0

        for degree_offset in range(-int(DynamicWindow.ANGLE_RANGE / 2),int(DynamicWindow.ANGLE_RANGE / 2),DynamicWindow.ANGLE_INCREMENT):
            angle = add_angle(math.radians(degree_offset),target_yaw)
            vector_x = force * math.cos(angle)
            vector_y = force * math.sin(angle)

            target_x = vector_x + x
            target_y = vector_y + y

            obstructed,clearance = DynamicWindow.calculate_obstruction(x,y,target_x,target_y,obstacles)
            score = 0
            #obstructed penalty
            if (obstructed):
                clearance = 0
                score -= DynamicWindow.OBSTRUCTION_PENALTY


            #Theoretically should not be negative unless path is obstructed
            clearance -= DynamicWindow.MIN_DISTANCE

            clearance = max(clearance,DynamicWindow.MAX_CLEARANCE)

            #greater clearance means greater weighting
            score += clearance * DynamicWindow.CLEARANCE_SCORE
            #greater angle offset, less score
            score += abs(degree_offset) * -DynamicWindow.ANGLE_PENALTY

            if (not degree_offset == DynamicWindow.current_angle):
                score -= DynamicWindow.MIN_CHANGE_PENALTY
                number_of_changes = abs(DynamicWindow.current_angle - degree_offset)
                score -= DynamicWindow.CHANGE_PENALTY * number_of_changes

            if (score > greatest_score):
                greatest_score = score
                goal_vector_x = vector_x
                goal_vector_y = vector_y
                best_path_clearance = min(max(clearance,0),DynamicWindow.VECTOR_STRENGTH)
                DynamicWindow.current_angle = degree_offset
        return vector_clamp(goal_vector_x,goal_vector_y,best_path_clearance)

class PathState():
    #States
    TURNING = "TURNING"
    WAITING = "WAITING"
    DRIVING = "DRIVING"
    STUCK = "STUCK"
    IDLE = "IDLE"

    #Checkpoints
    GOAL_REACHED = "GOAL_REACHED"
    DONE_WAITING = "DONE_WAITING"
    DONE_TURNING = "DONE_TURNING"

class Path:
    def __init__(self,x,y,yaw = 0):
        self.x = x
        self.y = y
        self.yaw = yaw
    def to_string(self,index):
        return f"{self.x},{self.y},{Path.index_to_status(index)},{self.yaw}"
    def index_to_status(index):
        if (index == 0):
            return MapKey.CURRENT_PATH.value
        return MapKey.PATH_IN_QUE.value

class Pathing:
    paths = []
    state = PathState.IDLE
    GOAL_DISTANCE_THRESHOLD = 10 #inches
    vector_x = 0
    vector_y = 0
    WAIT_TIME = 2

    timer = Timer()
    

    def paths_to_string():
        output = ""
        if (len(Pathing.paths) == 0):
            return output
        for i in range(len(Pathing.paths)):
            path = Pathing.paths[i]
            if (not isinstance(path,Path)):
                continue
            output += path.to_string(i) + "/"
        return output

    def status():
        return f'\n---PATHING---\nPath obstructed: {DynamicWindow.obstructed}\nState: {Pathing.state}'
    
    def calculate(x,y,yaw,obstacles):
        #No paths -> Dont go
        if (len(Pathing.paths) == 0):
            Pathing.vector_x = 0
            Pathing.vector_y = 0
            Pathing.state = PathState.IDLE
            return 0,0,PathState.IDLE
        if Pathing.state == PathState.WAITING:
        #Done waiting -> next path
            if Pathing.timer.time_passed() > Pathing.WAIT_TIME:
                Pathing.paths.pop(0)
                Pathing.state = PathState.IDLE
                return 0,0,PathState.DONE_WAITING
            else:
                return 0,0,PathState.WAITING
            
        
        target = Pathing.paths[0]
        if (not isinstance(target,Path)):
            return 0,0,PathState.IDLE
        tx = target.x
        ty = target.y
        target_yaw = target.yaw
        print("tx: ",tx," ty: ",ty, " tyaw: ",target_yaw)

        distance = math.sqrt(((tx - x) ** 2) + ((ty - y) ** 2))
        #Near goal -> Turn to target yaw
        if Pathing.state == PathState.TURNING:
            delta_yaw = shortest_angular_distance(yaw,target_yaw)
            turn = Drivetrain.calculate_turn(delta_yaw)
            #Near target yaw -> Wait
            if (abs(turn) < Drivetrain.MIN_TURN):
                Pathing.state = PathState.WAITING
                return 0,0,PathState.DONE_TURNING
            return turn,0,PathState.TURNING
        
        if (distance < Pathing.GOAL_DISTANCE_THRESHOLD):
            Pathing.timer.reset()
            Pathing.state = PathState.TURNING
            return 0,0,PathState.GOAL_REACHED
        
        
        Pathing.vector_x,Pathing.vector_y = DynamicWindow.calculate(x,y,yaw,tx,ty,obstacles)
        print("DW VECTORS",Pathing.vector_x,Pathing.vector_y)

        if (abs(Pathing.vector_x) < 1 and abs(Pathing.vector_y) < 1):
            return 0,0,PathState.STUCK
        
        turn,drive = Drivetrain.vector_to_drive(Pathing.vector_x,Pathing.vector_y,yaw)
        return turn,drive,PathState.DRIVING
