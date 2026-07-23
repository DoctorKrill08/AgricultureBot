import numpy as np
import math
from enum import Enum
from System.Constants import *
from System.Lidar import *
from System.interface_map import INCHES_PER_NODE
from timer import *

class Node():
    OBSTACLE = "O"
    SAVED_OBSTACLE = "S"
    EMPTY = "E"
    FORGET_TIME = 60
    def __init__(self,x : float,y : float,status = EMPTY, raw_x = None, raw_y = None):
        self.x  = x
        self.y = y
        self.status = status
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.id = Node.generate_id(x,y)
        self.timer = Timer()
    def generate_id(x,y):
        return str(x) + "," + str(y)
    def to_string(self):
        return self.id + "," + self.status
    def save_obstacle(self):
        self.timer.reset()
        self.status = Node.SAVED_OBSTACLE
    def is_obstacle(self):
        return self.status == Node.OBSTACLE or self.status == Node.SAVED_OBSTACLE

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
    def update(x,y,yaw,lidar_data):
        Map.calculate_visibility(x,y,yaw)
        for point in lidar_data:
            if (point == None):
                continue
            x,y = Map.point_to_node(point[0],point[1])
            x,y = point[0],point[1]
            id = Node.generate_id(x,y)
            if id in Map.nodes:
                node = Map.nodes[id]
                if (isinstance(node,Node)):
                    if (node.status == Node.OBSTACLE):
                        continue
            node = Node(x,y,Node.OBSTACLE,raw_x=point[0],raw_y=point[1])
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
            x,y = node.raw_x,node.raw_y
            if (x == None or y == None):
                delete_list[key] = node
                continue
            deltaX = x - bot_x
            deltaY = y - bot_y
            distance = math.sqrt((deltaX ** 2) + (deltaY ** 2))
            if (distance > Lidar.MAX_DISTANCE):
                delete_list[key] = node
                continue
            if (distance < Lidar.MIN_DISTANCE + Lidar.LIDAR_X):
                node.save_obstacle()
                continue
            angle = math.atan2(deltaY,deltaX)
            delta_yaw = abs(shortest_angular_distance(angle,yaw))
            if math.degrees(delta_yaw) > (Lidar.ANGLE_RANGE / 2):
                node.save_obstacle()
                continue

            #if moving to much save obstacles and continue
            #All obstacles beyond this are "theoretically visible"
            #The way we can clear obstacles that are theoretically visible is by seeing if the obstacle is farther than it should be
            #Otherwise, like if the obstacle is closer or not visible, it might or may not be there, so we keep it on the map
            
            delete_list[key] = node
        for key,node in delete_list.items():
            del Map.nodes[key]


        

        
    