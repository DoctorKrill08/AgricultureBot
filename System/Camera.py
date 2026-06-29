import pyrealsense2 as rs
import numpy as np
import cv2
import sys
from pathlib import Path
import math


def meters_to_inches(meters):
    return meters * 39.3701

class Camera:
    MIN_DISTANCE = 10 #inches
    TOO_CLOSE = 14 #inches
    FORWARD_VIEW_DISTANCE = 30
    FPS = 15
    distance = 0
    WIDTH = 640
    HEIGHT = 480
    CENTER_X = int(WIDTH / 2)
    CENTER_Y = int(HEIGHT / 2)
    WIDTH_RANGE = CENTER_X
    MAX_HEIGHT = HEIGHT - 200
    MIN_HEIGHT = 10
    SPACE_BETWEEN_RAYS = int(2)
    MIN_NUM_OF_CLOSE_POINTS = 50
    MIN_NUM_OF_VISIBLE_POINTS = 200
    too_close = False
    pipe = None
    on = False
    ROBOT_WIDTH = 20 #inches
    ROBOT_HEIGHT = 8
    CAMERA_Y = 5
    GROUND_HEIGHT = 2

    TURN_P = -1.5
    DRIVE_P = -0.2
    
    closest_distance = 0
    turn_vector = 0
    drive_vector = 0

    def status():
        return f"Camera on: {Camera.on} DriveP: {Camera.DRIVE_P}, TurnP: {Camera.TURN_P}"
    def yaw():
        return 0
    def start():
        Camera.angle = [0,0,0] #pitch roll yaw
        Camera.position = [0,0,0] #ground x, ground y, height

        try:
            Camera.pipe = rs.pipeline()
            cfg  = rs.config()

            cfg.enable_stream(rs.stream.color, Camera.WIDTH,Camera.HEIGHT, rs.format.bgr8, Camera.FPS)
            cfg.enable_stream(rs.stream.depth, Camera.WIDTH,Camera.HEIGHT, rs.format.z16, Camera.FPS)

            Camera.pipe.start(cfg)
            Camera.on = True
        except Exception as e:
            Camera.on = False
            print(e)
    def read():
        if (not Camera.on):
            return
        frame = Camera.pipe.wait_for_frames()
        depth_frame = frame.get_depth_frame()

        canvas_black = np.zeros((Camera.HEIGHT, Camera.WIDTH, 3), dtype=np.uint8)
        canvas_black[20, 20] = [0, 0, 255]
        Camera.pixels_within_distance(canvas_black,depth_frame)
            
        #cv2.imshow('to close', canvas_black)

    def stop():
        if (Camera.on == False):
            return
        Camera.pipe.stop()
        Camera.on = False
    def pixels_within_distance(canvas,depth_frame):
        depth_intrin = depth_frame.profile.as_video_stream_profile().get_intrinsics()
        obstacle_points = [] #horizontal distance (x), distance (z)
        visible_points = []
        close_points = []
        closest = {"x" : 0, "y": 0, "z_inches": 1000} #x,y,distance

        size = Camera.SPACE_BETWEEN_RAYS
        color = [0, 0, 255] #Red
        point_sum = 0
        for x in range(Camera.CENTER_X - Camera.WIDTH_RANGE, Camera.CENTER_X + Camera.WIDTH_RANGE, Camera.SPACE_BETWEEN_RAYS):
            for y in range(Camera.MIN_HEIGHT,Camera.MAX_HEIGHT, Camera.SPACE_BETWEEN_RAYS): 
                z_depth = depth_frame.get_distance(x,y)
                distance = meters_to_inches(z_depth)
                if (distance == 0):
                    continue
                visible_points.append({"x" : x, "y " : y, "z_inches" : z_depth})
                spatial_point = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], z_depth)
                horizontal_distance = meters_to_inches(spatial_point[0])  # X component inches
                verticial_distance = meters_to_inches(spatial_point[1])
                if abs(horizontal_distance) < Camera.ROBOT_WIDTH/2 and verticial_distance > -(Camera.ROBOT_HEIGHT - Camera.CAMERA_Y) and (verticial_distance - Camera.CAMERA_Y) < (Camera.GROUND_HEIGHT) and distance < Camera.FORWARD_VIEW_DISTANCE:
                    obstacle_points.append({"x" : x,"x_inches" : horizontal_distance,"z_inches" : distance})
                    if (distance < Camera.TOO_CLOSE):
                        close_points.append({"x" : x,"y" : y,"z_inches": distance})
                    if (distance < closest["z_inches"]):
                        closest = {"x" : x,"y" : y,"z_inches" : distance,"y_inches" : verticial_distance}
                    canvas[y-(size):y+(size), x-(size):x+(size)] = color
                    if (not x == Camera.CENTER_X):
                        point_sum += ((Camera.ROBOT_WIDTH/horizontal_distance) / distance)
                    
        if (len(obstacle_points) <= 0):
            avg = 0
        else:
            avg = point_sum / len(obstacle_points)
        Camera.turn_vector = avg * Camera.TURN_P
        Camera.drive_vector = Camera.DRIVE_P *((Camera.TOO_CLOSE / closest["z_inches"]))
        if (abs(Camera.turn_vector) < 0.05):
            Camera.turn_vector = 0
        if (abs(Camera.turn_vector) > 1):
            Camera.drive_vector = -1
        if (Camera.too_close):
            Camera.drive_vector = -1
        print("visible pixels: ",len(visible_points))
        print("too close pixels: ",len(close_points))
        size = 15

        color = [0,255,0]
        x = closest["x"]
        y = closest["y"]
        canvas[y-(size):y+(size), x-(size):x+(size)] = color
        if (len(close_points) > Camera.MIN_NUM_OF_CLOSE_POINTS):
            Camera.too_close = True
        elif (closest["z_inches"] > Camera.TOO_CLOSE and len(visible_points) > Camera.MIN_NUM_OF_VISIBLE_POINTS):
            Camera.too_close = False
            canvas[0:20,0:20] = [0,255,0]
        
if __name__ == "__main__":
    Camera.start()
    while True:
        Camera.read()
        if cv2.waitKey(1) == ord('q'):
            break
    Camera.stop()
