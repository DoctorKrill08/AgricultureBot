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
    g_star = 25 #Inches, what is the maximum effective radius of the force
    kR = 550 # repulsive force constant
    max_repulsive = 50
    repulsive_exponent = 0.21


    kA = 5
    attractive_exponent = 0.5
    max_attractive = 35

    chaos_force = 3
    chaos_min_distance = 10

    stuck_threshold = 1
    
    def calculate_chaos(x,y,yaw,tx,ty):
        delta_x = tx - x
        delta_y = ty - y
        distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
        force = distance / APF.chaos_min_distance
        if (force > APF.chaos_force):
            force = APF.chaos_force
        x = force * math.cos(yaw)
        y = force * math.sin(yaw)
        return x,y
    def calculate_attractive_vectors(x,y,tx,ty):
        vector_x = 0
        vector_y = 0
        delta_x = tx - x
        delta_y = ty - y
        force = math.sqrt((delta_x ** 2) + (delta_y ** 2))
        force = APF.kA * math.pow(force,APF.attractive_exponent)
        if force > APF.max_attractive:
            force = APF.max_attractive
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
            velocity = APF.kR * (((1 / g) ** APF.repulsive_exponent) - ((1 / APF.g_star) ** APF.repulsive_exponent))
            vector_x += velocity * -math.cos(angle)
            vector_y += velocity * -math.sin(angle)
            quantity += 1
        if (quantity > 1):
            vector_x /= quantity
            vector_y /= quantity
        vector_x,vector_y = vector_clamp(vector_x,vector_y,APF.max_repulsive)
        return vector_x,vector_y
    
    def is_stuck(vector_x,vector_y):
        return (abs(vector_x) + abs(vector_y) < APF.stuck_threshold)
             

class EdgeFinder:
    MAX_DISTANCE = 40
    MIN_DISTANCE = 1.5

    VECTOR_STRENGTH = 5
    
    UPDATE_RATE = 5
    current_tick = 0

    obstructed = False
    def is_obstacle_near_point(x,y,obstacles):
        for id,obstacle in obstacles.items():
            delta_x = obstacle.x - x
            delta_y = obstacle.y- y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < ROBOT_WIDTH / 2):
                return True
            else:
                continue
        return False

    def get_nearest_obstacles(target,obstacles):
        x = target.x
        y = target.y
        nearest = []
        nearest.append(target)
        for id,obstacle in obstacles.items():
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance < ROBOT_WIDTH and distance > EdgeFinder.MIN_DISTANCE):
                nearest.append(obstacle)
            else:
                continue
        return nearest

    def get_edges(x,y,obstacles):
        list = []
        for id,obstacle in obstacles.items():
            if (not isinstance(obstacle,Node)):
                continue
            if (not obstacle.is_obstacle()):
                continue
            delta_x = obstacle.x - x
            delta_y = obstacle.y - y
            distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
            if (distance > EdgeFinder.MAX_DISTANCE):
                continue
            if (distance < ROBOT_WIDTH / 2):
                continue
            nearest = EdgeFinder.get_nearest_obstacles(obstacle,obstacles)
            if (len(nearest) == 1):
                continue
            list.append(nearest)
        list = sorted(list,key = len)
        if (len(list) < 8):
            return list
        list = list[:int(0.2 * len(list))]
        return list
                
    def get_closest_edge(tx,ty,edges):
        min_distance = 10000
        closest = None
        for i in range(len(edges)):
            nearest = edges[i]
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
        edges = EdgeFinder.get_edges(x,y,obstacles)
        if len(edges) == 0:
            return None
        print("#edges:",len(edges))
        #get the obstacle thats closest to the target
        closest = EdgeFinder.get_closest_edge(tx,ty,edges)
        return closest
    def calculate_vectors(x,y,tx,ty,obstacles):
        EdgeFinder.current_tick += 1
        if (EdgeFinder.current_tick < EdgeFinder.UPDATE_RATE):
            return None,None
        EdgeFinder.current_tick = 0
        edge = EdgeFinder.calculate_closest_edge(x,y,tx,ty,obstacles)
        if (edge == None or not isinstance(edge,Node)):
            return 0,0
        delta_x = edge.x - x
        delta_y = edge.y - y
        strength = math.sqrt((delta_x ** 2) + (delta_y ** 2))
        if (strength > EdgeFinder.VECTOR_STRENGTH):
            strength = EdgeFinder.VECTOR_STRENGTH
        return vector_clamp(delta_x,delta_y,strength)
        

class PathingStatus():
    GOAL_REACHED = "GOAL_REACHED"
    DRIVING = "DRIVING"
    STUCK = "STUCK"
    IDLE = "IDLE"


class Pathing:
    EDGE = "EDGE"
    APF = "APF"
    mode = APF

    GOAL_DISTANCE_THRESHOLD = 10

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


            """ex,ey = EdgeFinder.calculate_vectors(x,y,tx,ty,obstacles)
            if not ex == None and not ey == None:
                Pathing.edge_vector_x = ex
                Pathing.edge_vector_y = ey
            print("EDGE VECTORS",Pathing.edge_vector_x,Pathing.edge_vector_y)"""

            Pathing.edge_vector_x,Pathing.edge_vector_y = APF.calculate_chaos(x,y,yaw,tx,ty)

            Pathing.vector_x = Pathing.goal_vector_x + Pathing.edge_vector_x + Pathing.obstacle_vector_x
            Pathing.vector_y = Pathing.goal_vector_y + Pathing.edge_vector_y + Pathing.obstacle_vector_y

            Pathing.vector_x,Pathing.vector_y = vector_clamp(Pathing.vector_x,Pathing.vector_y,max)
            print("NET VECTORS",Pathing.vector_x,Pathing.vector_y)

            if (APF.is_stuck(Pathing.vector_x,Pathing.vector_y)):
                return 0,0,PathingStatus.STUCK
            
            turn,drive = Drivetrain.vector_to_drive(Pathing.vector_x,Pathing.vector_y,yaw)
            return turn,drive,PathingStatus.DRIVING
        return 0,0,PathingStatus.IDLE
            

            
        
