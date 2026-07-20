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

class APF:
    g_star = 30 #Inches, what is the maximum effective radius of the force
    kR = 10000 # repulsive force constant
    turnR = -1.6

    kA = 1
    max_force = 30

    stuck_threshold = 1
    def calculate_attractive_vectors(x,y,tx,ty):
        vector_x = 0
        vector_y = 0
        delta_x = tx - x
        delta_y = ty - y
        force = APF.kA * math.sqrt((delta_x ** 2) + (delta_y ** 2))
        if force > APF.max_force:
            force = APF.max_force
        angle = math.atan2(delta_y,delta_x)
        vector_x = force * math.cos(angle)
        vector_y = force * math.sin(angle)
        return vector_x,vector_y

    def calculate_obstacle_vectors(x,y,yaw,obstacles):
        vector_x = 0
        vector_y = 0
        quantity = 0
        for id,obstacle in obstacles.items():
            if (not isinstance(obstacle,Node)):
                continue
            if (not obstacle.status == Node.OBSTACLE and not obstacle.status == Node.SAVED_OBSTACLE):
                continue
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y

            g = math.sqrt((delta_x ** 2) + (delta_y ** 2))

            if (g > APF.g_star):
                continue
            angle = math.atan2(delta_y,delta_x)
            velocity = APF.kR * (((1 / g) ** 2) - ((1 / APF.g_star) ** 2))
            vector_x += velocity * -math.cos(angle)
            vector_y += velocity * -math.sin(angle)
            quantity += 1
        if (quantity > 1):
            vector_x /= quantity
            vector_y /= quantity
        vector_x,vector_y = vector_clamp(vector_x,vector_y,APF.max_force)
        return vector_x,vector_y
    
    def is_stuck(vector_x,vector_y):
        return (abs(vector_x) + abs(vector_y) < APF.stuck_threshold)
             
        
class Bug:
    OBSTACLE_RADIUS = 10 #Inches
    target = None #The target the bug algorithm decides to drive to

    def target_visible(x,y,tx,ty):
        pass
    def calculate_tanget(x,y,obstacles):
        pass

class PathingStatus():
    GOAL_REACHED = "GOAL_REACHED"
    BUG_REACHED = "BUG_REACHED"
    DRIVING = "DRIVING"
    STUCK = "STUCK"
    IDLE = "IDLE"


class Pathing:
    BUG = "BUG"
    APF = "APF"
    mode = APF

    GOAL_DISTANCE_THRESHOLD = 5

    drive_vector_x = 0
    drive_vector_y = 0

    obstacle_vector_x = 0
    obstacle_vector_y = 0

    vector_x = 0
    vector_y = 0
    
    def calculate(x,y,yaw,tx,ty,obstacles):
        if (Pathing.mode == Pathing.APF):
            distance = math.sqrt(((tx - x) ** 2) + ((ty - y) ** 2))
            if (distance < Pathing.GOAL_DISTANCE_THRESHOLD):
                return 0,0,PathingStatus.GOAL_REACHED
            
            Pathing.drive_vector_x,Pathing.drive_vector_y = APF.calculate_attractive_vectors(x,y,tx,ty)
            Pathing.obstacle_vector_x,Pathing.obstacle_vector_y = APF.calculate_obstacle_vectors(x,y,yaw,obstacles)
            print("DRIVE VECTORS",Pathing.drive_vector_x,Pathing.drive_vector_y)
            print("OBSTACLE VECTORS",Pathing.obstacle_vector_x,Pathing.obstacle_vector_y)


            Pathing.vector_x = Pathing.drive_vector_x + Pathing.obstacle_vector_x
            Pathing.vector_y = Pathing.drive_vector_y + Pathing.obstacle_vector_y

            Pathing.vector_x,Pathing.vector_y = vector_clamp(Pathing.vector_x,Pathing.vector_y,APF.max_force)
            print("NET VECTORS",Pathing.vector_x,Pathing.vector_y)

            if (APF.is_stuck(Pathing.vector_x,Pathing.vector_y)):
                return 0,0,PathingStatus.STUCK
            
            turn,drive = Drivetrain.vector_to_drive(Pathing.vector_x,Pathing.vector_y,yaw)
            return turn,drive,PathingStatus.DRIVING
        return 0,0,PathingStatus.IDLE
            

            
        
