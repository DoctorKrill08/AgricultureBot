import math
from enum import Enum
from turtle import st

from System.Constants import *
from System.Drivetrain import Drivetrain
from System.interface_map import MapKey
from System.mapping import Node
from timer import Timer


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

    MAX_VECTOR_STRENGTH = 30
    MIN_VECTOR_STRENGTH = 5

    ANGLE_INCREMENT = 10 #Degrees
    ANGLE_RANGE = 270 #Degrees

    ANGLE_PENALTY = 0.1
    CLEARANCE_SCORE = 3
    CHANGE_PENALTY = 1.5
    MIN_CHANGE_PENALTY = 5


    OBSTRUCTION_PENALTY = 100000

    MIN_CLEARANCE = ROBOT_WIDTH / 2
    MAX_CLEARANCE = 20

    obstructed = False
    current_angle = 0

    DEFAULT_SCORE = 500
    SCORE_TO_STRENGTH_RATIO = 0.5

    REMAP_TIME = 0.3
    DRIVE_TIME = 1.5

    timer = Timer()
    remapping = False
    @staticmethod
    def score_to_strength(score):
        return max(min((DynamicWindow.DEFAULT_SCORE + score) * DynamicWindow.SCORE_TO_STRENGTH_RATIO,DynamicWindow.MAX_VECTOR_STRENGTH),DynamicWindow.MIN_VECTOR_STRENGTH)
    @staticmethod
    def calculate_clearance(x,y,obstacles):
        obstructed = False
        clearance = 1000000
        for id,obstacle in obstacles.items():
            if (not isinstance(obstacle,Node)):
                continue
            if (not obstacle.is_obstacle()):
                continue
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < clearance):
                clearance = distance
            if (distance < DynamicWindow.MIN_CLEARANCE):
                obstructed = True
            continue
        return obstructed,clearance
    @staticmethod
    def calculate_obstruction(bot_x,bot_y,angle,check_distance : float,obstacles):
        if (check_distance > 40):
            check_distance = 40
        check_distance -= (ROBOT_WIDTH / 2)
        furthest = 0
        increment = DynamicWindow.MIN_CLEARANCE / 2
        i = 0
        clearance = 100000
        obstructed = False
        complete = False
        if (check_distance < increment):
            return obstructed,clearance
        while not complete and not obstructed:
            furthest = i * increment
            i += 1
            if (furthest > check_distance):
                furthest = check_distance
            x = bot_x + (furthest * math.cos(angle))
            y = bot_y + (furthest * math.sin(angle))

            obstructed,this_clearance = DynamicWindow.calculate_clearance(x,y,obstacles)
            if (this_clearance < clearance):
                clearance = this_clearance
            if (obstructed):
                complete = True
            if furthest == check_distance:
                complete = True
        return obstructed,clearance

    @staticmethod
    def calculate(x,y,yaw,tx,ty,obstacles):
        delta_x = tx - x
        delta_y = ty - y
        target_yaw = math.atan2(delta_y,delta_x)
        distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
        #print("distance: ",distance, " target_yaw: ", target_yaw)

        obstructed,clearance = DynamicWindow.calculate_obstruction(x,y,target_yaw,distance,obstacles)
        force = min(distance,DynamicWindow.MAX_VECTOR_STRENGTH)
        if (obstructed and not DynamicWindow.obstructed):
            DynamicWindow.timer.reset()

        DynamicWindow.obstructed = obstructed
        if (not DynamicWindow.obstructed):
            best_path_clearance =  -10000
            DynamicWindow.current_angle = 0
            goal_vector_x = force * math.cos(target_yaw)
            goal_vector_y = force * math.sin(target_yaw)
            return goal_vector_x,goal_vector_y
        if (not DynamicWindow.remapping and DynamicWindow.timer.time_passed() > DynamicWindow.DRIVE_TIME):
            DynamicWindow.remapping = True
            DynamicWindow.timer.reset()
            return 0,0
        if (DynamicWindow.remapping and not DynamicWindow.timer.time_passed() > DynamicWindow.REMAP_TIME):
            return 0,0
        if (DynamicWindow.remapping and DynamicWindow.timer.time_passed() > DynamicWindow.REMAP_TIME):
            DynamicWindow.remapping = False
            DynamicWindow.timer.reset()
        goal_vector_x = 0
        goal_vector_y = 0

        greatest_score = -100000000
        best_path_clearance = 0
        best_path_degree_offset = 0

        for degree_offset in range(-int(DynamicWindow.ANGLE_RANGE / 2),int(DynamicWindow.ANGLE_RANGE / 2) + DynamicWindow.ANGLE_INCREMENT,DynamicWindow.ANGLE_INCREMENT):
            angle = math.radians(degree_offset) + target_yaw
            vector_x = force * math.cos(angle)
            vector_y = force * math.sin(angle)

            obstructed,clearance = DynamicWindow.calculate_obstruction(x,y,angle,distance,obstacles)
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

            if (degree_offset != DynamicWindow.current_angle):
                score -= DynamicWindow.MIN_CHANGE_PENALTY
                number_of_changes = abs(DynamicWindow.current_angle - degree_offset)
                score -= DynamicWindow.CHANGE_PENALTY * number_of_changes
            #print("angle: ",angle," degree offset: ", degree_offset, "score: ",score)
            if (score > greatest_score):
                greatest_score = score
                goal_vector_x = vector_x
                goal_vector_y = vector_y
                #best_path_clearance = min(max(clearance,0),DynamicWindow.MAX_VECTOR_STRENGTH)
                best_path_degree_offset = degree_offset
        print("---greatest  score---: ", greatest_score)
        DynamicWindow.current_angle = best_path_degree_offset
        return vector_clamp(goal_vector_x,goal_vector_y,DynamicWindow.score_to_strength(greatest_score))

class PathState:
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
    @staticmethod
    def index_to_status(index):
        if (index == 0):
            return MapKey.CURRENT_PATH.value
        return MapKey.PATH_IN_QUE.value

class Pathing:
    paths = []
    state = PathState.IDLE
    GOAL_DISTANCE_THRESHOLD = 5 #inches
    vector_x = 0
    vector_y = 0
    WAIT_TIME = 1
    TURN_TIME = 1.5

    timer = Timer()

    @staticmethod
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

    @staticmethod
    def status():
        return f'\n---PATHING---\nPath obstructed: {DynamicWindow.obstructed}\nState: {Pathing.state}\nANGLE_INCREMENT:{DynamicWindow.ANGLE_INCREMENT}\nANGLE_PENALTY:{DynamicWindow.ANGLE_PENALTY}\nCLEARANCE_SCORE:{DynamicWindow.CLEARANCE_SCORE}\nCHANGE_PENALTY:{DynamicWindow.CHANGE_PENALTY}\nMAX_CLEARANCE:{DynamicWindow.MAX_CLEARANCE}'

    @staticmethod
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
            if (abs(turn) < Drivetrain.MIN_TURN and Pathing.timer.time_passed() > Pathing.TURN_TIME):
                Pathing.state = PathState.WAITING
                return 0,0,PathState.DONE_TURNING
            return turn,0,PathState.TURNING

        if (distance < Pathing.GOAL_DISTANCE_THRESHOLD):
            Pathing.timer.reset()
            Pathing.state = PathState.TURNING
            return 0,0,PathState.GOAL_REACHED


        Pathing.vector_x,Pathing.vector_y = DynamicWindow.calculate(x,y,yaw,tx,ty,obstacles)
        #print("DW VECTORS",Pathing.vector_x,Pathing.vector_y)

        if (abs(Pathing.vector_x) < 1 and abs(Pathing.vector_y) < 1):
            return 0,0,PathState.STUCK

        turn,drive = Drivetrain.vector_to_drive(Pathing.vector_x,Pathing.vector_y,yaw)
        return turn,drive,PathState.DRIVING
