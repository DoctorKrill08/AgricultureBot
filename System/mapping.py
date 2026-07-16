import numpy as np
import math
from enum import Enum
from System.Constants import *
from System.interface_map import *
import numpy as np
from timer import *

class Node():
    OBSTACLE = "O"
    OBSTACLE_ADJACENT = "A"
    SAVED_OBSTACLE = "S"
    EMPTY = "E"
    TARGET = "T"

    FORGET_TIME = 10
    OBSTACLE_NODE_CLEARANCE = 1

    def is_a_visible_obstacle(self):
        return self.status == Node.OBSTACLE or self.status == Node.OBSTACLE_ADJACENT
    def find_node(x,y):
        ix,iy = Map.point_to_indices(x,y)
        return Map.nodes[ix][iy]
    def __init__(self,x : float,y : float,status = "E", raw_x = 0, raw_y = 0):
        self.x  = x
        self.y = y
        self.status = status
        self.raw_x = raw_x
        self.raw_y = raw_y
        self.timer = Timer()
    def to_string(self):
        return str(self.x) + "," + str(self.y) + "," + self.status
    def make_obstacle(self):
        self.status = Node.OBSTACLE
        self.timer.reset()
        start_ix,start_iy = Map.point_to_indices(self.x,self.y)
        for ix in range(start_ix-Node.OBSTACLE_NODE_CLEARANCE,start_ix + Node.OBSTACLE_NODE_CLEARANCE + 1):
            if (ix < 0 or ix > len(Map.nodes) - 1):
                continue
            for iy in range(start_iy - Node.OBSTACLE_NODE_CLEARANCE,start_iy + Node.OBSTACLE_NODE_CLEARANCE + 1):
                if (iy < 0 or iy > len(Map.nodes[ix]) - 1):
                    continue
                node = Map.nodes[ix][iy]
                if node is self:
                    continue
                if (not isinstance(node,Node)):
                    continue
                if (not node.status == Node.OBSTACLE):
                    node.status = Node.OBSTACLE_ADJACENT
                    node.timer.reset()
        
    def save_obstacle(self):
        self.status = Node.SAVED_OBSTACLE
        self.timer.reset()
    def clear(self):
        self.status = Node.EMPTY
        self.raw_x = 0
        self.raw_y = 0

class Map:
    INCHES_PER_NODE = INCHES_PER_NODE
    nodes =  None
    MAX_MAP_DISTANCE = 100 #Inches
    loaded = False
    def start():
        length = (2 * (Map.MAX_MAP_DISTANCE)) // Map.INCHES_PER_NODE
        Map.nodes = [[None for _ in range(length)] for _ in range(length)]

        for x in range(-Map.MAX_MAP_DISTANCE,Map.MAX_MAP_DISTANCE + Map.INCHES_PER_NODE, Map.INCHES_PER_NODE):
            for y in range(-Map.MAX_MAP_DISTANCE,Map.MAX_MAP_DISTANCE + Map.INCHES_PER_NODE, Map.INCHES_PER_NODE):
                ix,iy = Map.point_to_indices(x,y)
                Map.nodes[ix][iy] = Node(x,y)
        Map.loaded = True
    def print_nodes():
        telemetry = ""
        for row in Map.nodes:
            for node in row:
                if (not isinstance(node,Node)):
                    continue
                if (node.status == Node.EMPTY):
                    continue
                telemetry += node.to_string() + "/"
        return telemetry
    def status():
        telemetry = "\n---MAP---\n"
        return telemetry
    def point_to_indices(x,y):
        ix = round((x + Map.MAX_MAP_DISTANCE) / Map.INCHES_PER_NODE)
        iy = round((y + Map.MAX_MAP_DISTANCE) / Map.INCHES_PER_NODE)

        max_index = len(Map.nodes) - 1
        ix = max(0, min(ix, max_index))
        iy = max(0, min(iy, max_index))

        return ix, iy
    
    def update(x,y,yaw,camera_array):
        if (not Map.loaded):
            return
        Map.calculate_visibility(x,y,yaw)
        for point in camera_array:
            if (point == None):
                continue
            horizontal = point[0]
            forward = point[1]
            Map.add_obstacle(x,y,horizontal,forward,yaw)
    def add_obstacle(x,y,horizontal,forward,yaw=0):
        if (horizontal == None or forward == None):
            return
        d = math.sqrt((horizontal ** 2) + (forward ** 2))
        d = d + CAMERA_DISTANCE_FROM_ROBOT
        if d >= Map.MAX_MAP_DISTANCE:
            return
        relative_angle = math.atan2(horizontal,forward)
        if math.degrees(abs(relative_angle)) + 15 > CAMERA_HORIZONTAL_FOV / 2:
            return

        angle = add_angle(yaw,relative_angle)

        delta_x = d * math.cos(angle)
        delta_y = d * math.sin(angle)
        node = Node.find_node(delta_x,delta_y)
        node.raw_x = x + delta_x
        node.raw_y = y + delta_y
        if (not isinstance(node,Node)):
            return
        node.make_obstacle()
    #Look at each obstacle node and determine its visibility
    #Run this after add obstacles
    def calculate_visibility(x,y,yaw=0):
        if len(Map.nodes) <= 0:
            return
        for row in Map.nodes:
            for node in row:
                if (not isinstance(node,Node)):
                    continue
                if (node.timer.time_passed() > Node.FORGET_TIME and node.status == Node.SAVED_OBSTACLE):
                    node.clear()
                    continue
                if node.status == Node.EMPTY:
                    continue

                delta_x  = x - node.raw_x
                delta_y = y - node.raw_y
                distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
                if (distance > Map.MAX_MAP_DISTANCE):
                    node.clear()
                    continue
                
                angle = math.atan2(delta_y,delta_x)
                delta_yaw = abs(shortest_angular_distance(angle,yaw))

                #If the node is NOT theoretically viewable
                if (math.degrees(delta_yaw) + 15 > (CAMERA_HORIZONTAL_FOV / 2)):
                    if (node.status == Node.SAVED_OBSTACLE):
                        #Recalculate pre existing points
                        ix,iy = Map.point_to_indices(delta_x,delta_y)
                        start_time = node.timer.start_time
                        raw_x = node.raw_x
                        raw_y = node.raw_y
                        calculated_node = Map.nodes[ix][iy]
                        if (node is calculated_node):
                            node.status = Node.SAVED_OBSTACLE
                            print("calculated node is the same")
                            continue
                        node = calculated_node
                        if (not isinstance(node,Node)):
                            continue
                        if (not node.is_a_visible_obstacle()):
                            node.timer.start_time = start_time
                            node.status = Node.SAVED_OBSTACLE
                            node.raw_x = raw_x
                            node.raw_y = raw_y
                            continue
                    #Save visible obstacles
                    if (node.is_a_visible_obstacle()):
                        node.save_obstacle()
                        continue
                    continue
                elif node.status == Node.SAVED_OBSTACLE:
                    node.clear()
                    continue
                
                    
                #All obstacles beyond this are "theoretically visible"
                #The way we can clear obstacles that are theoretically visible is by seeing if the obstacle is farther than it should be
                #Otherwise, like if the obstacle is closer or not visible, it might or may not be there, so we keep it on the map
                node.clear()

        

        
    