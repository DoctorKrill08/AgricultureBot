import pyrealsense2 as rs
import numpy as np
import cv2
import sys
from pathlib import Path


def meters_to_inches(meters):
    return meters * 39.3701

class Camera:
    PERIOD = .1
    MIN_DISTANCE = 25 #inches
    FPS = 15
    distance = 0
    WIDTH = 640
    HEIGHT = 480
    CENTER_X = int(WIDTH / 2)
    CENTER_Y = int(HEIGHT / 2)
    WIDTH_RANGE = 300
    MAX_HEIGHT = HEIGHT - 100
    MIN_HEIGHT = 100
    SPACE_BETWEEN_RAYS = int(8)
    MIN_NUM_OF_CLOSE_RAYS = 30
    to_close = False
    pipe = None
    on = False
    ROBOT_WIDTH = 20 #inches
    
    closest_distance = 0
    turn_vector = 0
    drive_vector = 0

    def status():
        return f"Camera on: {Camera.on}"
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
        closest = {"x" : 0, "y": 0, "z_inches": 1000} #x,y,distance

        size = Camera.SPACE_BETWEEN_RAYS
        color = [0, 0, 255] #Red
        for x in range(Camera.CENTER_X - Camera.WIDTH_RANGE, Camera.CENTER_X + Camera.WIDTH_RANGE, Camera.SPACE_BETWEEN_RAYS):
            for y in range(Camera.MIN_HEIGHT,Camera.MAX_HEIGHT, Camera.SPACE_BETWEEN_RAYS): 
                z_depth = depth_frame.get_distance(x,y)
                distance = meters_to_inches(z_depth)
                if (distance == 0):
                    continue
                spatial_point = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], z_depth)
                horizontal_distance = meters_to_inches(spatial_point[0])  # X component inches

                if distance < Camera.MIN_DISTANCE and abs(horizontal_distance) < Camera.ROBOT_WIDTH/2:
                    obstacle_points.append({"x" : x,"x_inches" : horizontal_distance,"z_inches" : distance})
                    if (distance < closest["z_inches"]):
                        closest = {"x" : x,"y" : y,"z_inches" : distance}
                    canvas[y-(size):y+(size), x-(size):x+(size)] = color

        #Put all the obstacle points in a line such that no x pixels repeat, filtered by distance
        obstacle_points,sum = Camera.get_point_line(obstacle_points)
            
        
        
        avg = sum / len(obstacle_points)
        kP = -25
        Camera.turn_vector = avg * kP
        Camera.drive_vector = 0.1 *(closest["z_inches"] - 10)
        print("drive: ",Camera.drive_vector,"turn: ",Camera.turn_vector)
        size = 15

        color = [0,255,0]
        x = closest["x"]
        y = closest["y"]
        canvas[y-(size):y+(size), x-(size):x+(size)] = color
        if (len(obstacle_points) > Camera.MIN_NUM_OF_CLOSE_RAYS):
            Camera.to_close = True
        else:
            Camera.to_close = False
            canvas[0:20,0:20] = [0,255,0]
    
    def get_point_line(obstacle_points):
        #Input a 3D array -> {x -> pixels, x_inches -> real world horizontal offset, z_inches, real world forward distance}
        #Returns a filtered array with no x duplicates, filtered by distance (z). Also returns weighted (by distance) sum
        point_line = []
        sum = 0
        for point in obstacle_points:
            matches = [item for item in obstacle_points if item["x"] == point["x"]] 
            #No matches ? -> no change
            closest_match = point
            if len(matches) == 1:
                point_line.append(closest_match)
            else:
                for compare_point in matches:
                    if (compare_point["z_inches"] > closest_match["z_inches"]):
                        closest_match = compare_point
                point_line.append(closest_match)
            #Sum weighting determined by distance (inverse)
            #Sum positions based on delta x pixels from center of camera
            sum += ((Camera.CENTER_X - compare_point["x"]) / compare_point["z_inches"])
        return point_line,sum
        
if __name__ == "__main__":
    Camera.start()
    while True:
        Camera.read()
        if cv2.waitKey(1) == ord('q'):
            break
    Camera.stop()
