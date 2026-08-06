import base64
import os
from posix import stat
import sys
from enum import Enum

import cv2
import numpy as np
import pyrealsense2 as rs
from fastapi import FastAPI, WebSocket

from System.Constants import *
from timer import *


class Camera:
    FPS = 15
    distance = 0
    WIDTH = 640
    HEIGHT = 480
    CENTER_X = int(WIDTH / 2)
    CENTER_Y = int(HEIGHT / 2)
    WIDTH_RANGE = CENTER_X - 40
    MIN_HEIGHT = HEIGHT - 30
    MAX_HEIGHT = 30
    SPACE_BETWEEN_RAYS : int = 10
    MIN_NUM_OF_CLOSE_POINTS = 120
    OBSTRUCTED_PIXEL_THRESHOLD = 1500
    obstructed = False
    vision_pipe = None
    imu_pipe = None
    on = False

    TURN_P = 1.5
    DRIVE_P = -0.1

    closest_distance = 0
    closest = []

    relative_goal_angle = 0

    turn = 0
    drive = 0

    IMU_enabled = False

    raw_accel_reading = np.array([0,0,0])
    raw_gyro_reading = np.array([0,0,0])

    prev_frame = None
    canvas = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)

    binary_frame : bytes = b""

    @staticmethod
    def exception():
        ctx = rs.context()
        devices = ctx.query_devices()

        if not devices:
            print("CRITICAL: No RealSense devices detected at all. Check your USB cable/port connection.")
        else:
            try:
                dev = devices[0]
                print(f"Device found: {dev.get_info(rs.camera_info.name)}")
                print(f"Serial Number: {dev.get_info(rs.camera_info.serial_number)}")

                # Check sensors directly
                for sensor in dev.query_sensors():
                    sensor_name = sensor.get_info(rs.camera_info.name)
                    # We only care about the Motion Module (IMU)
                    if "Motion" in sensor_name:
                        print(f"\nFound Sensor: {sensor_name}")
                        for profile in sensor.get_stream_profiles():
                            print(f"  Stream: {profile.stream_name()} | FPS: {profile.fps()} | Format: {profile.format()}")
            except:
                print("Camera not found")

    @staticmethod
    def status():
        return f"\n-----CAMERA-----\nCamera on: {Camera.on}\nOBSTRUCTED: {Camera.obstructed}"
    @staticmethod
    def start():
        Camera.angle = [0,0,0] #pitch roll yaw
        Camera.position = [0,0,0] #ground x, ground y, height
        Camera.vision_pipe = rs.pipeline()
        Camera.imu_pipe = rs.pipeline()
        imu_cfg = rs.config()
        vision_cfg = rs.config()
        try:
            imu_cfg.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 250)
            imu_cfg.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 400)
            Camera.imu_pipe.start(imu_cfg)
            Camera.IMU_enabled = True
            print("IMU CONNECTED")
        except Exception as e:
            Camera.IMU_enabled = False
            Camera.exception()
            print("IMU NOT CONNECTED", e)

        try:
            vision_cfg.enable_stream(rs.stream.color, Camera.WIDTH,Camera.HEIGHT, rs.format.bgr8, Camera.FPS)
            vision_cfg.enable_stream(rs.stream.depth, Camera.WIDTH,Camera.HEIGHT, rs.format.z16, Camera.FPS)
            Camera.vision_pipe.start(vision_cfg)
            Camera.on = True
            print("CAMERA CONNECTED")
        except Exception as e:
            Camera.on = False
            Camera.exception()
            print("CAMERA NOT CONNECTED", e)


    UPDATE_FRAME_RATE = 2
    current_frame = 0
    @staticmethod
    def update():
        if (not Camera.on):
            Camera.obstructed = True
            return
        Camera.current_frame += 1
        if (Camera.current_frame < Camera.UPDATE_FRAME_RATE):
            return
        Camera.current_frame = 0
        frame = Camera.vision_pipe.wait_for_frames()
        depth_frame = frame.get_depth_frame()
        color_frame = frame.get_color_frame()

       # depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        #depth_cm = cv2.applyColorMap(cv2.convertScaleAbs(depth_image,alpha = 0.03), cv2.COLORMAP_JET)

        _, buffer = cv2.imencode('.jpg', color_image, [cv2.IMWRITE_JPEG_QUALITY, 70])
        Camera.binary_frame = buffer.tobytes()

        #cv2.imshow('depth', depth_cm)
        #cv2.imshow('rgb', color_image)

        blacklisted_pixels,blacklist_image = Camera.filter_camera(depth_frame)
        """ cv2.imshow('blacklist', blacklist_image)

        colored_pixels_mask = np.any(blacklist_image > 0, axis=-1)
        result = depth_image.copy()
        result[colored_pixels_mask] = 0
        result = cv2.applyColorMap(cv2.convertScaleAbs(result,
                                        alpha = 0.03), cv2.COLORMAP_JET)
        cv2.imshow('filtered', result)"""

        Camera.closest = Camera.closest_pixels_1D(depth_frame,blacklisted_pixels)
        if (len(blacklisted_pixels) > Camera.OBSTRUCTED_PIXEL_THRESHOLD):
            Camera.obstructed = True
        else:
            Camera.obstructed = False

        if (Camera.IMU_enabled):
            Camera.raw_accel_reading = None
            Camera.raw_gyro_reading = None
            imu_frame = Camera.imu_pipe.wait_for_frames()
            accel_frame = imu_frame.first_or_default(rs.stream.accel)
            if accel_frame:
                accel_data = accel_frame.as_motion_frame().get_motion_data()
                array =  np.array([0,0,0], dtype=np.float32)
                array[IMU.LEFT] = accel_data.x
                array[IMU.DOWN] = accel_data.y
                array[IMU.FORWARD] = accel_data.z
                Camera.raw_accel_reading = array
                #print(f"Accel: x={accel_data.x:.3f}, y={accel_data.y:.3f}, z={accel_data.z:.3f}")

            # Get Gyroscope data
            gyro_frame = imu_frame.first_or_default(rs.stream.gyro)
            if gyro_frame:
                gyro_data = gyro_frame.as_motion_frame().get_motion_data()
                array =  np.array([0,0,0], dtype=np.float32)
                array[IMU.ROLL] = gyro_data.z
                array[IMU.PITCH] = -gyro_data.x
                array[IMU.YAW] = gyro_data.y
                Camera.raw_gyro_reading = array
                #print(f"Gyro: x={gyro_data.x:.3f}, y={gyro_data.y:.3f}, z={gyro_data.z:.3f}")
        #cv2.imshow('to close', canvas_black)
    @staticmethod
    def stop():
        if (Camera.on == False):
            return
        Camera.vision_pipe.stop()
        Camera.on = False
    @staticmethod
    def blacklist(x,y,blacklist_array):
        key = str(x) + "," + str(y)
        blacklist_array[key] = [x,y]
        return blacklist_array
    @staticmethod
    def paint_on_canvas(canvas,x,y,size,color = [0,0,255]):
        canvas[y-(size):y+(size), x-(size):x+(size)] = color
        return canvas
    @staticmethod
    def filter_camera(depth_frame):
        depth_image = np.asanyarray(depth_frame.get_data())
        blacklisted_pixels = {}
        blacklist_image = np.zeros((Camera.HEIGHT, Camera.WIDTH,3), dtype=np.uint8)
        if (Camera.prev_frame == None):
            Camera.prev_frame = depth_frame
            return blacklisted_pixels,depth_image
        for x in range(Camera.CENTER_X - Camera.WIDTH_RANGE, Camera.CENTER_X + Camera.WIDTH_RANGE, Camera.SPACE_BETWEEN_RAYS):
            for y in range(Camera.MAX_HEIGHT,Camera.MIN_HEIGHT, Camera.SPACE_BETWEEN_RAYS):
                z = meters_to_inches(depth_frame.get_distance(x,y))
                prev_z = meters_to_inches(Camera.prev_frame.get_distance(x,y))
                if (z <= CAMERA_MIN_DEPTH  or prev_z <= CAMERA_MIN_DEPTH):
                    blacklist_image = Camera.paint_on_canvas(blacklist_image,x,y,Camera.SPACE_BETWEEN_RAYS,[0,255,255])
                    blacklisted_pixels = Camera.blacklist(x,y,blacklisted_pixels)
                    continue
                delta_z = z - prev_z
                if (abs(delta_z) > 15):
                    blacklist_image = Camera.paint_on_canvas(blacklist_image,x,y,Camera.SPACE_BETWEEN_RAYS,[0,0,255])
                    blacklisted_pixels = Camera.blacklist(x,y,blacklisted_pixels)
                    continue
        Camera.prev_frame = depth_frame
        return blacklisted_pixels,blacklist_image
    @staticmethod
    def closest_pixels_1D(depth_frame,blacklisted_pixels = None):
        depth_intrin = depth_frame.profile.as_video_stream_profile().get_intrinsics()
        closest_y = 1000
        #Forward,Horizontal
        points_1D = [None] * Camera.WIDTH
        avg_range = round(Camera.SPACE_BETWEEN_RAYS / 2)
        x_start = Camera.CENTER_X - Camera.WIDTH_RANGE
        x_end = Camera.CENTER_X + Camera.WIDTH_RANGE
        y_start = Camera.MAX_HEIGHT
        y_end = Camera.MIN_HEIGHT

        prev_horizontal = 0
        for x in range(x_start, x_end, Camera.SPACE_BETWEEN_RAYS):
            closest_y = 1000
            for y in range(y_start,y_end, Camera.SPACE_BETWEEN_RAYS):
                if (not blacklisted_pixels == None):
                    key = str(x) + "," + str(y)
                    if key in blacklisted_pixels:
                        continue
                z_depth = depth_frame.get_distance(x,y)
                if (z_depth == None):
                    continue
                spatial_point = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], (z_depth))
                z_depth = meters_to_inches(z_depth)
                horizontal_distance = meters_to_inches(spatial_point[0])
                vertical_distance = meters_to_inches(spatial_point[1])


                if (z_depth > closest_y):
                    continue
                if (z_depth < CAMERA_MIN_DEPTH):
                    continue
                if (vertical_distance < -4):
                    continue

                delta_horizontal = horizontal_distance - prev_horizontal
                if (abs(delta_horizontal) < 1):
                    continue
                prev_horizontal = horizontal_distance

                #For averaging, make sure neighboring vertical pixels EXIST

                average_y_start = y - avg_range
                average_y_end = y + avg_range
                if average_y_start < y_start:
                    continue
                if average_y_end > y_end:
                    continue
                average_depth = z_depth
                quantity = 1
                for y_compare in range(average_y_start, average_y_end):
                    key = str(x) + "," + str(y_compare)
                    if key in blacklisted_pixels:
                        continue
                    z_compare = (depth_frame.get_distance(x,y_compare))
                    if (z_compare == None):
                        continue
                    z_compare = meters_to_inches(z_compare)
                    if (z_compare < CAMERA_MIN_DEPTH):
                        continue
                    average_depth += z_compare
                    quantity += 1
                average_depth /= quantity
                z_depth = average_depth

                if (z_depth < closest_y):
                    closest_y = z_depth
                    points_1D[x] = [horizontal_distance,z_depth]
        return points_1D

class IMU:

    LEFT = 0 #X
    DOWN = 1 #Y
    FORWARD = 2 #Z

    ROLL = 0
    PITCH = 1
    YAW = 2

#Windows: python -m System.Camera
if __name__ == "__main__":
    Camera.start()
    while True:
        Camera.update()
        if cv2.waitKey(1) == ord('q'):
            break
    Camera.stop()
