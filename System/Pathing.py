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
    kR = 8000 # repulsive force constant

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
            if (not obstacle.is_obstacle()):
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
        vector_x,vector_y = vector_clamp(vector_x,vector_y,APF.max_force + 5)
        return vector_x,vector_y
    
    def is_stuck(vector_x,vector_y):
        return (abs(vector_x) + abs(vector_y) < APF.stuck_threshold)
             

class EdgeFinder:
    MAX_DISTANCE = 40

    VECTOR_STRENGTH = 10

    obstructed = False
    def is_obstacle_near_point(x,y,obstacles):
        for id,obstacle in obstacles.items():
            delta_x = obstacle.x - x
            delta_y = obstacle.y- y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < ROBOT_WIDTH):
                return True
            else:
                continue
        return False

    def get_nearest_obstacles(target : Node,obstacles):
        x = target.x
        y = target.y
        nearest = []
        nearest[0] = target
        for id,obstacle in obstacles.items():
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < ROBOT_WIDTH):
                nearest.append(obstacle)
            else:
                continue
        return nearest

    def sort_obstacles(x,y,obstacles):
        list = []
        for id,obstacle in obstacles.items():
            if (not isinstance(obstacle,Node)):
                continue
            if (not obstacle.is_obstacle()):
                continue
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < EdgeFinder.MAX_DISTANCE):
                continue
            nearest = EdgeFinder.get_nearest_obstacles(obstacle,obstacles)
            if (len(nearest) == 1):
                continue
            list.append(nearest)
        list = sorted(list,key = len)
        return list
                
    def get_edges(sorted_obstacles):
        split_index = 0
        can_split = False
        for i in range(len(sorted_obstacles)):
            nearest = sorted_obstacles[i]
            if (len(nearest) > 3):
                can_split = True
                split_index = i
                break
        if (not can_split):
            return sorted_obstacles
        return sorted_obstacles.slice(0,split_index + 1)
    def get_closest_edge(tx,ty,windows):
        min_distance = 10000
        closest = None
        for i in range(len(windows)):
            nearest = windows[i]
            obstacle = nearest[0]
            delta_x = tx - obstacle.x
            delta_y = ty - obstacle.y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < min_distance):
                min_distance = distance
                closest = obstacle
        return closest

    def calculate_obstruction(bot_x,bot_y,target_x,target_y,obstacles):
        delta_x = target_x - bot_x
        delta_y = target_y - bot_y
        
        angle = math.atan2(delta_y,delta_x)

        check_distance = 40
        furthest = 0
        increment = ROBOT_WIDTH
        i = 0
        obstructed = False
        while furthest < check_distance and not obstructed:
            i += 1
            furthest = i * increment
            x = furthest * math.cos(angle)
            y = furthest * math.sin(angle)
            obstructed = EdgeFinder.is_obstacle_near_point(x,y,obstacles)
            if (obstructed):
                break
        return obstructed
    def calculate_closest_edge(x,y,tx,ty,obstacles):
        if (len(obstacles) == 0):
            return None
        EdgeFinder.obstructed = EdgeFinder.calculate_obstruction(x,y,tx,ty,obstacles)
        if (not EdgeFinder.obstructed):
            return None 
        #For each obstacle, find adjacent obstacles, then sort an array based on the amount of adjacent obstacles each obstacle has
        edges = EdgeFinder.sort_obstacles(x,y,obstacles)
        #Filter out obstacles with a lot of adjacent obstacles (more than 3)
        edges = EdgeFinder.get_edges(edges)
        if len(edges) == 0:
            return None
        #get the obstacle thats closest to the target
        closest = EdgeFinder.get_closest_edge(tx,ty,edges)
        return closest
    def calculate_vectors(x,y,tx,ty,obstacles):
        edge = EdgeFinder.calculate_closest_edge(x,y,tx,ty,obstacles)
        if (edge == None or not isinstance(edge,Node)):
            return 0,0
        delta_x = edge.x - x
        delta_y = edge.y - y
        return vector_clamp(delta_x,delta_y,EdgeFinder.VECTOR_STRENGTH)
        

class PathingStatus():
    GOAL_REACHED = "GOAL_REACHED"
    DRIVING = "DRIVING"
    STUCK = "STUCK"
    IDLE = "IDLE"


class Pathing:
    EDGE = "EDGE"
    APF = "APF"
    mode = APF

    GOAL_DISTANCE_THRESHOLD = 5

    goal_vector_x = 0
    goal_vector_y = 0

    edge_vector_x = 0
    edge_vector_y = 0

    obstacle_vector_x = 0
    obstacle_vector_y = 0

    vector_x = 0
    vector_y = 0
    def status():
        return f'\n---PATHING---\nPath obstructed: {EdgeFinder.obstructed}'
    
    def calculate(x,y,yaw,tx,ty,obstacles):
        if (Pathing.mode == Pathing.APF):
            distance = math.sqrt(((tx - x) ** 2) + ((ty - y) ** 2))
            if (distance < Pathing.GOAL_DISTANCE_THRESHOLD):
                return 0,0,PathingStatus.GOAL_REACHED
            
            Pathing.goal_vector_x,Pathing.goal_vector_y = APF.calculate_attractive_vectors(x,y,tx,ty)

            max = math.sqrt((Pathing.goal_vector_x ** 2) + (Pathing.goal_vector_y ** 2))

            Pathing.obstacle_vector_x,Pathing.obstacle_vector_y = APF.calculate_obstacle_vectors(x,y,yaw,obstacles)
            print("DRIVE VECTORS",Pathing.goal_vector_x,Pathing.goal_vector_y)
            print("OBSTACLE VECTORS",Pathing.obstacle_vector_x,Pathing.obstacle_vector_y)


            Pathing.edge_vector_x,Pathing.edge_vector_y = EdgeFinder.calculate_vectors(x,y,tx,ty,obstacles)

            #TODO add edge vector logic
            Pathing.vector_x = Pathing.goal_vector_x + Pathing.obstacle_vector_x
            Pathing.vector_y = Pathing.goal_vector_y + Pathing.obstacle_vector_y

            Pathing.vector_x,Pathing.vector_y = vector_clamp(Pathing.vector_x,Pathing.vector_y,max)
            print("NET VECTORS",Pathing.vector_x,Pathing.vector_y)

            if (APF.is_stuck(Pathing.vector_x,Pathing.vector_y)):
                return 0,0,PathingStatus.STUCK
            
            turn,drive = Drivetrain.vector_to_drive(Pathing.vector_x,Pathing.vector_y,yaw)
            return turn,drive,PathingStatus.DRIVING
        return 0,0,PathingStatus.IDLE
            

            
        
