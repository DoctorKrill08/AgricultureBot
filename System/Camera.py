import pyrealsense2 as rs
import numpy as np
import cv2
import sys
from pathlib import Path
#from ahrs.filters import Madgwick

# Adds 'my_project' (the grandparent of this file) to the python path
parent_dir = str(Path(__file__).resolve().parents[1])
sys.path.append(parent_dir)

from System.timer import *

def meters_to_inches(meters):
    return meters * 39.3701
class Camera:
    PERIOD = .1
    MIN_DISTANCE = 20 #inches
    FPS = 30
    distance = 0
    WIDTH = 640
    HEIGHT = 480
    CENTER_X = int(WIDTH / 2)
    CENTER_Y = int(HEIGHT / 2)
    WIDTH_RANGE = 100
    MAX_HEIGHT = HEIGHT - 100
    MIN_HEIGHT = 100
    SPACE_BETWEEN_RAYS = int(8)
    MIN_NUM_OF_CLOSE_RAYS = 30
    to_close = False
    pipe = None
    on = False
    timer = Timer()

    angle = [0,0,0] #pitch roll yaw
    position = [0,0,0] #ground x, ground y, height

    def status():
        return f"Camera on: {Camera.on}\n Pitch: {np.degrees(Camera.angle[0])} \n Roll: {np.degrees(Camera.angle[1])} Yaw: {np.degrees(Camera.angle[2])}"
    def yaw():
        return Camera.angle[2]
    def reset_imu():
        Camera.angle = [0,0,0]
    def start():
        Camera.angle = [0,0,0] #pitch roll yaw
        Camera.position = [0,0,0] #ground x, ground y, height

        try:
            Camera.pipe = rs.pipeline()
            cfg  = rs.config()

            cfg.enable_stream(rs.stream.color, Camera.WIDTH,Camera.HEIGHT, rs.format.bgr8, Camera.FPS)
            cfg.enable_stream(rs.stream.depth, Camera.WIDTH,Camera.HEIGHT, rs.format.z16, Camera.FPS)
            cfg.enable_stream(rs.stream.accel)
            cfg.enable_stream(rs.stream.gyro)

            Camera.pipe.start(cfg)
            Camera.on = True
            Camera.timer.reset()
        except:
            Camera.on = False
    def read():
        Camera.to_close = False
        if (not Camera.on):
            return
        #if (Camera.timer.time_passed() < Camera.PERIOD):
            #time.sleep(Camera.PERIOD - Camera.timer.time_passed())
        frame = Camera.pipe.wait_for_frames()
        depth_frame = frame.get_depth_frame()

        canvas_black = np.zeros((Camera.HEIGHT, Camera.WIDTH, 3), dtype=np.uint8)
        canvas_black[20, 20] = [0, 0, 255]
        Camera.pixels_within_distance(canvas_black,depth_frame)

        accel_frame = frame.first_or_default(rs.stream.accel)
        gyro_frame = frame.first_or_default(rs.stream.gyro)

        if accel_frame and gyro_frame:
            accel_data = accel_frame.as_motion_frame().get_motion_data()
            gyro_data = gyro_frame.as_motion_frame().get_motion_data()


            # Gyro data (angular velocity)
            gyro = np.array([gyro_data.x, gyro_data.z, gyro_data.y])
            accel = np.array([accel_data.x, accel_data.z, accel_data.y + 9.81])
            
            # Integrate angular velocity to get angles
            Camera.angle += gyro * Camera.timer.time_passed()
            #deltaAngle = Camera.angle - gyro * Camera.timer.time_passed()
            Camera.position += (accel * (Camera.timer.time_passed() ** 2))

            print(f"Angle (Degrees) - Pitch: {np.degrees(Camera.angle[0]):.2f}, Roll: {np.degrees(Camera.angle[1]):.2f}, Yaw: {np.degrees(Camera.angle[2]):.2f}, DT: {Camera.timer.time_passed()}")
            print(f"Position (meters?) - X: {meters_to_inches(Camera.position[0]):.2f}, Y: {meters_to_inches(Camera.position[1]):.2f}, Z: {meters_to_inches(Camera.position[2]):.2f}")
            Camera.timer.reset()

        #cv2.imshow('to close', canvas_black)

    def stop():
        Camera.pipe.stop()
        Camera.on = False
    def pixels_within_distance(canvas,depth_frame):
        close_rays = 0
        for x in range(Camera.CENTER_X - Camera.WIDTH_RANGE, Camera.CENTER_X + Camera.WIDTH_RANGE, Camera.SPACE_BETWEEN_RAYS):
            for y in range(Camera.MIN_HEIGHT,Camera.MAX_HEIGHT, Camera.SPACE_BETWEEN_RAYS): 
                distance = meters_to_inches(depth_frame.get_distance(x, y))
                if (distance == 0):
                    continue
                if distance < Camera.MIN_DISTANCE:
                    close_rays = close_rays + 1
                    canvas[y-(Camera.SPACE_BETWEEN_RAYS):y+(Camera.SPACE_BETWEEN_RAYS), x-(Camera.SPACE_BETWEEN_RAYS):x+(Camera.SPACE_BETWEEN_RAYS)] = [0, 0, 255]
        if (close_rays > Camera.MIN_NUM_OF_CLOSE_RAYS):
            Camera.to_close = True
        else:
            canvas[0:20,0:20] = [0,255,0]


        
if __name__ == "__main__":
    Camera.start()
    while True:
        Camera.read()
        if cv2.waitKey(1) == ord('q'):
            break
    Camera.stop()
