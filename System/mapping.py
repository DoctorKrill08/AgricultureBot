import numpy as np
import math
from enum import Enum
from System.Constants import *
from timer import *

class Node():
    OBSTACLE = "O"
    SAVED_OBSTACLE = "S"
    EMPTY = "E"
    FORGET_TIME = 10
    def __init__(self,x : float,y : float,status = EMPTY, raw_horizontal = 0, raw_forward = 0):
        self.x  = x
        self.y = y
        self.status = status
        self.raw_horizontal = raw_horizontal
        self.raw_forward = raw_forward
        self.id = str(x) + "," + str(y)
        self.timer = Timer()
    def to_string(self):
        return self.id + "," + self.status

class Map:
    MAX_DISTANCE = 70 #Inches
    nodes =  {}
    visible_obstacles = {}
    def print_nodes(nodes):
        telemetry = ""
        for id, node in nodes.items():
            if node == None or node == "" or not isinstance(node,Node):
                return
            telemetry += f"{node.to_string()}/" 
        return telemetry
    def status():
        telemetry = "\n---MAP---\n"
        telemetry += "NODES:\n"
        telemetry += Map.print_nodes(Map.nodes)
        telemetry += "\nVISIBLE:\n"
        telemetry += Map.print_nodes(Map.visible_obstacles)
    def clear():
        Map.visible_obstacles = {}
    def point_to_node(x,y):
        return x,y
        x = round_nearest(x,Map.INCHES_PER_NODE)
        y = round_nearest(y,Map.INCHES_PER_NODE)
        return x,y
    def update(x,y,yaw,camera_array):
        Map.clear()
        Map.calculate_visibility(x,y,yaw)
        for point in camera_array:
            if (point == None):
                continue
            horizontal = point[0]
            forward = point[1]
            Map.add_obstacle(horizontal,forward,x,y,yaw)
    def add_obstacle(horizontal,forward,x=0,y=0,yaw=0):
        if (horizontal == None or forward == None):
            return
        d = math.sqrt((horizontal ** 2) + (forward ** 2))
        d = d + CAMERA_DISTANCE_FROM_ROBOT
        if d <= 0:
            #what
            return
        if d >= Map.MAX_DISTANCE:
            return
        relative_angle = math.atan2(horizontal,forward)
        if math.degrees(abs(relative_angle)) + 15 > CAMERA_HORIZONTAL_FOV / 2:
            return

        angle = add_angle(yaw,relative_angle)

        x += d * math.cos(angle)
        y += d * math.sin(angle)
        x,y = Map.point_to_node(x,y)

        node = Node(x,y,Node.OBSTACLE,raw_horizontal=horizontal,raw_forward=forward)
        Map.visible_obstacles[node.id] = node
        Map.nodes[node.id] = node

    #Look at each obstacle node and determine its visibility
    #Run this after add obstacles
    def calculate_visibility(bot_x=0,bot_y=0,yaw=0):
        if len(Map.nodes) <= 0:
            return
        delete_list = {}
        for key,node in Map.nodes.items():
            if (not isinstance(node,Node)):
                delete_list[key] = node
                continue
            if (node.timer.time_passed() > Node.FORGET_TIME):
                delete_list[key] = node
                continue
            if node.status == Node.EMPTY:
                delete_list[key] = node
                continue
            x,y = node.x,node.y
            deltaX = x - bot_x
            deltaY = y - bot_y
            distance = math.sqrt((deltaX ** 2) + (deltaY ** 2))
            if (distance > CAMERA_MAX_DEPTH):
                node.status = Node.SAVED_OBSTACLE
                continue
            angle = math.atan2(deltaY,deltaX)
            delta_yaw = abs(shortest_angular_distance(angle,yaw))
            if math.degrees(delta_yaw) + 15 > (CAMERA_HORIZONTAL_FOV / 2):
                node.status = Node.SAVED_OBSTACLE
                continue
            #All obstacles beyond this are "theoretically visible"
            #The way we can clear obstacles that are theoretically visible is by seeing if the obstacle is farther than it should be
            #Otherwise, like if the obstacle is closer or not visible, it might or may not be there, so we keep it on the map
            delete_list[key] = node
        for key,node in delete_list.items():
            del Map.nodes[key]


        

        
    