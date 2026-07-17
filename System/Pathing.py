import math
from System.mapping import Node
from System.subsystems import Drivetrain
from enum import Enum
class APF:
    g_star = 20 #Inches, what is the maximum effective radius of the force
    kR = 10 # repulsive force constant

    kA = 1
    max_attractive = 20 #Max length of attractive vector

    stuck_threshold = 1
    def calculate_attractive_vectors(x,y,tx,ty):
        vector_x = 0
        vector_y = 0
        delta_x = tx - x
        delta_y = ty - y
        force = APF.kA * math.sqrt((delta_x ** 2) + (delta_y ** 2))
        if force > APF.max_attractive:
            force = APF.max_attractive
        angle = math.atan2(delta_y,delta_x)
        vector_x = force * math.cos(angle)
        vector_y = force * math.sin(angle)
        return vector_x,vector_y

    def calculate_obstacle_vectors(x,y,obstacles):
        vector_x = 0
        vector_y = 0
        quantity = 0
        for obstacle in obstacles:
            if (not isinstance(obstacle,Node)):
                continue
            if (not obstacle.status == Node.OBSTACLE and not obstacle.status == Node.SAVED_OBSTACLE):
                continue
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            g = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (g < APF.g_star):
                continue
            velocity = APF.kR * ((1 / g) - (1 / APF.g_star))
            if velocity > APF.max_attractive:
                velocity = APF.max_attractive
            angle = math.atan2(delta_y,delta_x)
            vector_x += velocity * math.cos(angle)
            vector_y += velocity * math.sin(angle)
            quantity += 1
        if (quantity > 1):
            vector_x /= quantity
            vector_y /= quantity
        return -vector_x,-vector_y
    
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
    
    def calculate(x,y,yaw,tx,ty,obstacles):
        if (Pathing.mode == Pathing.APF):
            distance = math.sqrt(((tx - x) ** 2) + ((ty - y) ** 2))
            if (distance < Pathing.GOAL_DISTANCE_THRESHOLD):
                return 0,0,PathingStatus.GOAL_REACHED
            
            drive_vector_x,drive_vector_y = APF.calculate_attractive_vectors(x,y,tx,ty)
            obstacle_vector_x,obstacle_vector_y = APF.calculate_obstacle_vectors(x,y,obstacles)

            vector_x = drive_vector_x + obstacle_vector_x
            vector_y = drive_vector_y + obstacle_vector_y

            if (APF.is_stuck(vector_x,vector_y)):
                return 0,0,PathingStatus.STUCK
            
            turn,drive = Drivetrain.vector_to_drive(vector_x,vector_y,yaw)
            return turn,drive,PathingStatus.DRIVING
        return 0,0,PathingStatus.IDLE
            

            
        
