import numpy as np
import math
from enum import Enum
from System.Constants import *
from System.Lidar import *
from System.interface_map import INCHES_PER_NODE,MapKey
from timer import *

EMPTY = MapKey.EMPTY.value
OBSTACLE = MapKey.OBSTACLE.value
SAVED_OBSTACLE = MapKey.SAVED_OBSTACLE.value

class Node():
    DEFAULT_CONFIDENCE = 300
    def __init__(self,x : float,y : float,status = EMPTY, raw_x = None, raw_y = None):
        self.x  = x
        self.y = y
        self.status = status
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.id = Node.generate_id(x,y)
        self.confidence = Node.DEFAULT_CONFIDENCE
    def generate_id(x,y):
        return str(x) + "," + str(y)
    def to_string(self):
        return self.id + "," + self.status
    def save_obstacle(self):
        if (self.status == SAVED_OBSTACLE):
            return
        self.confidence = Node.DEFAULT_CONFIDENCE
        self.status = SAVED_OBSTACLE
    def is_obstacle(self):
        return self.status == OBSTACLE or self.status == SAVED_OBSTACLE
    

class Map:
    MAX_DISTANCE = 40 #Inches
    nodes =  {}
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
    def point_to_node(x,y):
        x = round_nearest(x,INCHES_PER_NODE)
        y = round_nearest(y,INCHES_PER_NODE)
        return x,y
    def add_obstacle(horizontal,forward,x=0,y=0,yaw=0):
        if (horizontal == None or forward == None):
            return
        d = math.sqrt((horizontal ** 2) + (forward ** 2))
        d = d + CAMERA_DISTANCE_FROM_ROBOT
        if d <= CAMERA_DISTANCE_FROM_ROBOT + CAMERA_MIN_DEPTH:
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
        rounded_x,rounded_y = Map.point_to_node(x,y)

        node = Node(rounded_x,rounded_y,OBSTACLE,raw_x = x, raw_y = y)
        Map.nodes[node.id] = node

    def update(x,y,yaw,lidar_data,camera_data = None,rotational_movement = 0):
        Map.calculate_visibility(x,y,yaw,rotational_movement)
        for point in lidar_data:
            if (point == None):
                continue
            x,y = Map.point_to_node(point[0],point[1])
            x,y = point[0],point[1]
            id = Node.generate_id(x,y)
            if id in Map.nodes:
                node = Map.nodes[id]
                if (isinstance(node,Node)):
                    if (node.status == OBSTACLE):
                        continue
            node = Node(x,y,OBSTACLE,raw_x=point[0],raw_y=point[1])
            Map.nodes[node.id] = node
        for point in camera_data:
            if (point == None):
                continue
            horizontal = point[0]
            forward = point[1]
            Map.add_obstacle(horizontal,forward,x,y,yaw)
            
    #Look at each obstacle node and determine its visibility
    #Run this after add obstacles
    def calculate_visibility(bot_x=0,bot_y=0,yaw=0,rotational_movement = 0):
        if len(Map.nodes) <= 0:
            return
        delete_list = {}
        for key,node in Map.nodes.items():
            if (not isinstance(node,Node)):
                delete_list[key] = node
                continue
            if (node.confidence < 0):
                delete_list[key] = node
                continue
            if node.status == Node.EMPTY:
                delete_list[key] = node
                continue
            x,y = node.raw_x,node.raw_y
            if (x == None or y == None):
                delete_list[key] = node
                continue
            deltaX = x - bot_x
            deltaY = y - bot_y
            distance = math.sqrt((deltaX ** 2) + (deltaY ** 2))
            #passive confidence decay
            if (node.status == SAVED_OBSTACLE):
                node.confidence -= 0.01
            if (distance > CAMERA_MAX_DEPTH):
                node.save_obstacle()
                continue
            if (distance < CAMERA_MIN_DEPTH + CAMERA_DISTANCE_FROM_ROBOT):
                node.save_obstacle()
                continue
            angle = math.atan2(deltaY,deltaX)
            delta_yaw = abs(shortest_angular_distance(angle,yaw))
            if math.degrees(delta_yaw) > (Lidar.ANGLE_RANGE / 2):
                node.save_obstacle()
                continue
            if (node.status == SAVED_OBSTACLE):
                node.confidence -= 0.02 * max((0.5 / rotational_movement),1)
            elif(node.status == OBSTACLE):
                node.save_obstacle()
        for key,node in delete_list.items():
            del Map.nodes[key]


        

        
    