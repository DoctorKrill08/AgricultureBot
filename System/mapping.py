import numpy as np
import math
from enum import Enum
from System.Angle import *


ROBOT_WIDTH = 20 #inches
ROBOT_HEIGHT = 8
CAMERA_Y = 5
CAMERA_DISTANCE_FROM_ROBOT = 10
GROUND_HEIGHT = 2
CAMERA_FOV = 87 #Degrees
CAMERA_MAX_DEPTH = 3 # Meters

class Node(Enum):
    OBSTACLE = "OBSTACLE"
    EMPTY = "EMPTY"
    def __init__(self,x,y,status = EMPTY):
        self.x  = x
        self.y = y
        self.status = status
        self.id = str(x) + "," + str(y)
    def to_string(self):
        return self.id + "," + self.status

class Map:
    INCHES_PER_NODE = 2
    nodes =  {}
    visible_obstacles = {}
    def print_nodes(nodes):
        for node in Map.nodes:
            telemetry += f"{node.to_string()}/" 
    def status():
        telemetry = "NODES:\n"
        for node in Map.nodes:
            telemetry += f"{node.to_string()}/" 
        telemetry += "\nVISIBLE:\n"
        for node in Map.nodes:
            telemetry += f"{node.to_string()}/" 
    def clear():
        Map.visible_obstacles = {}
    def point_to_node(x,y):
        threshold = Map.INCHES_PER_NODE / 2

        round = x % Map.INCHES_PER_NODE
        difference = Map.INCHES_PER_NODE - abs(round)
        if (x > 0):
            if (round > threshold):
                x += difference
            else:
                x -= difference
        else:
            if (round > threshold):
                x -= difference
            else:
                x += difference

        round = y % Map.INCHES_PER_NODE
        difference = Map.INCHES_PER_NODE - abs(round)
        if (y > 0):
            if (round > threshold):
                y += difference
            else:
                y -= difference
        else:
            if (round > threshold):
                y -= difference
            else:
                y += difference
        return x,y
    def update(x,y,yaw):
        #make visible obstacle list
        #Calculate whether or not prior obstacles exist
        pass

    def add_obstacle(horizontal,forward,x=0,y=0,yaw=0):
        d = math.sqrt(horizontal ** 2, forward ** 2)
        d = d - CAMERA_DISTANCE_FROM_ROBOT
        if d <= 0:
            #what
            return
        relative_angle = math.atan2(horizontal,forward)
        angle = add_angle(relative_angle,yaw)

        x += d * math.cos(angle)
        y += d * math.sin(angle)
        x,y = Map.point_to_node(x,y)

        node = Node(x,y,Node.OBSTACLE)
        Map.visible_obstacles[node.id] = node

    #Look at each obstacle node and determine its visibility
    #Run this after add obstacles
    def calculate_visibility(bot_x=0,bot_y=0,yaw=0):
        for node in map.nodes:
            if not node.status == Node.OBSTACLE:
                continue
            x,y = node.x,node.y
            deltaX = x - bot_x
            deltaY = y - bot_y
            distance = math.sqrt((deltaX ** 2) + (deltaY ** 2))
            if (distance > CAMERA_MAX_DEPTH):
                continue
            angle = math.atan2(deltaY,deltaX)
            delta_yaw = abs(shortest_angular_distance(angle,yaw))
            if (delta_yaw) > math.radians(CAMERA_FOV / 2):
                continue
            #All obstacles beyond this are "theoretically visible"
            #The way we can clear obstacles that are theoretically visible is by seeing if the obstacle is farther than it should be
            #Otherwise, like if the obstacle is closer or not visible, it might or may not be there, so we keep it on the map
            


        

        
    