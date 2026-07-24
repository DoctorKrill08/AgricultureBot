import math
from System.mapping import Node
from System.subsystems import Drivetrain
from System.Constants import *
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

    ANGLE_PENALTY = 0.1
    CLEARANCE_SCORE = 0.8

    OBSTRUCTION_PENALTY = 100

    MIN_CLEARANCE = ROBOT_WIDTH / 2
    MAX_CLEARANCE = 20

    obstructed = False

    def calculate_clearance(x,y,obstacles):
        obstructed = False
        clearance = 1000000
        for id,obstacle in obstacles.items():
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < clearance):
                clearance = distance
            if (distance < DynamicWindow.MIN_CLEARANCE):
                obstructed = True
            continue
        return obstructed,clearance

    def calculate_obstruction(bot_x,bot_y,target_x,target_y,obstacles):
        delta_x = target_x - bot_x
        delta_y = target_y - bot_y
        
        angle = math.atan2(delta_y,delta_x)

        check_distance = 40
        furthest = 0
        increment = ROBOT_WIDTH
        i = 0
        clearance = 100000
        obstructed = False
        while furthest < check_distance and not obstructed:
            i += 1
            furthest = i * increment
            x = furthest * math.cos(angle)
            y = furthest * math.sin(angle)
            obstructed,this_clearance = DynamicWindow.calculate_clearance(x,y,obstacles)
            if (this_clearance < clearance):
                clearance = this_clearance
            if (obstructed):
                break
        return obstructed
    
    
    def calculate(x,y,yaw,tx,ty,obstacles):
        delta_x = tx - x
        delta_y = ty - y
        target_yaw = math.atan2(delta_y,delta_x)
        distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))

        DynamicWindow.obstructed,clearance = DynamicWindow.calculate_obstruction(x,y,tx,ty,obstacles)
        
        if (not DynamicWindow.obstructed):
            force = max(distance,DynamicWindow.VECTOR_STRENGTH)

            goal_vector_x = force * math.cos(target_yaw)
            goal_vector_y = force * math.sin(target_yaw)
            return goal_vector_x,goal_vector_y

        goal_vector_x = 0
        goal_vector_y = 0

        greatest_score = -10000
        best_path_clearance = 0

        for degree_offset in range(-(DynamicWindow.ANGLE_RANGE / 2),(DynamicWindow.ANGLE_RANGE / 2),DynamicWindow.ANGLE_INCREMENT):
            angle = angle_wrap(math.radians(degree_offset) + target_yaw)
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

            if (score > greatest_score):
                greatest_score = score
                goal_vector_x = vector_x
                goal_vector_y = vector_y
                best_path_clearance = max(min(clearance,0),DynamicWindow.VECTOR_STRENGTH)

        return vector_clamp(goal_vector_x,goal_vector_y,best_path_clearance)

class PathingStatus():
    GOAL_REACHED = "GOAL_REACHED"
    DRIVING = "DRIVING"
    STUCK = "STUCK"
    IDLE = "IDLE"


class Pathing:
    GOAL_DISTANCE_THRESHOLD = 10
    vector_x = 0
    vector_y = 0

    def status():
        return f'\n---PATHING---\nPath obstructed: {DynamicWindow.obstructed}'
    
    def calculate(x,y,yaw,tx,ty,obstacles):
        if (Pathing.mode == Pathing.APF):
            distance = math.sqrt(((tx - x) ** 2) + ((ty - y) ** 2))
            if (distance < Pathing.GOAL_DISTANCE_THRESHOLD):
                return 0,0,PathingStatus.GOAL_REACHED
            
            Pathing.vector_x,Pathing.vector_y = DynamicWindow.calculate(x,y,yaw,tx,ty,obstacles)
            print("DW VECTORS",Pathing.vector_x,Pathing.vector_y)

            if (abs(Pathing.vector_x) < 1 or abs(Pathing.vector_y) < 1):
                return 0,0,PathingStatus.STUCK
            
            turn,drive = Drivetrain.vector_to_drive(Pathing.vector_x,Pathing.vector_y,yaw)
            return turn,drive,PathingStatus.DRIVING
        return 0,0,PathingStatus.IDLE