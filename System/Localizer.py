from timer import *
def meters_to_inches(meters):
    return meters * 39.3700787402
import math
import matplotlib.pyplot as plt
from enum import Enum
from System.GPS import *
import numpy as np
import cv2
import sys
from pathlib import Path
from System.hardware import *
from System.mapping import Map
from System.Angle import *
import time

import os
import sys

# Inject your local Release folder to the top of the search path
sys.path.insert(0, os.path.expanduser('~/librealsense/build/Release/'))
os.environ["LD_LIBRARY_PATH"] = os.path.expanduser('~/librealsense/build/Release/') + ":" + os.environ.get("LD_LIBRARY_PATH", "")

import pyrealsense2 as rs


class Camera:
    TOO_CLOSE = 12 #inches
    FPS = 15
    distance = 0
    WIDTH = 640
    HEIGHT = 480
    CENTER_X = int(WIDTH / 2)
    CENTER_Y = int(HEIGHT / 2)
    WIDTH_RANGE = CENTER_X
    MAX_HEIGHT = HEIGHT - 200
    MIN_HEIGHT = 10
    SPACE_BETWEEN_RAYS = int(4)
    MIN_NUM_OF_CLOSE_POINTS = 120
    MIN_NUM_OF_VISIBLE_POINTS = 6000
    too_close = False
    vision_pipe = None
    imu_pipe = None
    on = False

    TURN_P = 1.5
    DRIVE_P = -0.1
    
    closest_distance = 0

    relative_goal_angle = 0
    
    turn = 0
    drive = 0

    IMU_enabled = False

    raw_accel_reading = np.array([0,0,0])
    raw_gyro_reading = np.array([0,0,0])

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


    def status():
        return f"\n-----CAMERA-----\nCamera on: {Camera.on}\nTOO CLOSE: {Camera.too_close}\nDriveP: {Camera.DRIVE_P}\nTurnP: {Camera.TURN_P}\nTURN: {Camera.turn}\nDRIVE: {Camera.drive}\nVECTOR[0]: {Camera.drive_vector[0]}\nVector[1]: {Camera.drive_vector[1]}"
    def start():
        
        ctx = rs.context()
        try:
            dev = ctx.query_devices()[0]
            serial = dev.get_info(rs.camera_info.serial_number)
        except:
            return

        Camera.angle = [0,0,0] #pitch roll yaw
        Camera.position = [0,0,0] #ground x, ground y, height
        Camera.vision_pipe = rs.pipeline()
        Camera.imu_pipe = rs.pipeline()
        imu_cfg = rs.config()
        vision_cfg = rs.config()
        try:
            imu_cfg.enable_device(serial)
            imu_cfg.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 250)
            imu_cfg.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 400)
            Camera.imu_pipe.start(imu_cfg)
            Camera.IMU_enabled = True
            IMU.start()
            print("IMU CONNECTED")
        except Exception as e:
            Camera.IMU_enabled = False
            Camera.exception()
            print("IMU NOT CONNECTED", e)

        try:
            vision_cfg.enable_device(serial)
            vision_cfg.enable_stream(rs.stream.color, Camera.WIDTH,Camera.HEIGHT, rs.format.bgr8, Camera.FPS)
            vision_cfg.enable_stream(rs.stream.depth, Camera.WIDTH,Camera.HEIGHT, rs.format.z16, Camera.FPS)
            Camera.vision_pipe.start(vision_cfg)
            Camera.on = True
            print("CAMERA CONNECTED")
        except Exception as e:
            Camera.on = False
            Camera.exception()
            print("CAMERA NOT CONNECTED", e)
    def calculate_vectors(yaw,mult):
        T = Camera.turn
        D = Camera.drive
        print("YAW:", yaw)
        alpha = -math.atan2(T,mult)
        print("ALPHA: ",alpha)

        theta = yaw + alpha
        print("THETA: ",theta)

        R = math.sqrt((T ** 2)+ (mult ** 2)) + D
        if R < 0:
            R = 0
        print("D: ",D)
        print("R: ",R)
        print("mult",mult)

        Camera.drive_vector = np.array([R * math.cos(theta),R * math.sin(theta)])

        

    def read():
        if (not Camera.on):
            return
        frame = Camera.vision_pipe.wait_for_frames()
        depth_frame = frame.get_depth_frame()

        canvas_black = np.zeros((Camera.HEIGHT, Camera.WIDTH, 3), dtype=np.uint8)
        canvas_black[20, 20] = [0, 0, 255]
        closest = Camera.closest_pixels_1D(depth_frame)
        Map.clear()
        for point in closest:
            horizontal = point[0]
            forward = point[1]
            Map.add_obstacle(horizontal,forward,Localizer.x,Localizer.y,Localizer.yaw)
        

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
            
        IMU.run(Camera.raw_accel_reading,Camera.raw_gyro_reading)
            
        #cv2.imshow('to close', canvas_black)

    def stop():
        if (Camera.on == False):
            return
        Camera.vision_pipe.stop()
        Camera.on = False
    def closest_pixels_1D(depth_frame):
        depth_intrin = depth_frame.profile.as_video_stream_profile().get_intrinsics()
        closest_y = 1000
        #Forward,Horizontal
        points_1D = []
        for x in range(Camera.CENTER_X - Camera.WIDTH_RANGE, Camera.CENTER_X + Camera.WIDTH_RANGE, Camera.SPACE_BETWEEN_RAYS):
            for y in range(Camera.MIN_HEIGHT,Camera.MAX_HEIGHT, Camera.SPACE_BETWEEN_RAYS): 
                z_depth = depth_frame.get_distance(x,y)
                z_distance = meters_to_inches(z_depth)
                spatial_point = rs.rs2_deproject_pixel_to_point(depth_intrin, [x, y], z_depth)
                horizontal_distance = meters_to_inches(spatial_point[0])
                if (z_distance < closest_y):
                    closest_y = z_distance
                    points_1D[x] = [horizontal_distance,z_distance]
        return points_1D                
    


class IMUState(Enum):
    DISABLED = "DISABLED"
    CONFIG_ANGLE = "CONFIG_ANGLE"
    CONFIG_ERROR = "CONFIG_ERROR"
    ACTIVE = "ACTIVE"

class IMU():
    state = IMUState.DISABLED


    def add_angle(a,b):
        return a + b

    POSITION = 0
    ROTATE = 1

    ACCEL_VARIANCE = np.array([20,20,20],dtype=np.float32)

    state_variance = np.array([1000.0,1000.0,1000.0])

    gravity = 386.089 #Inches per second^2

    accel = np.array([0.0,0.0,0.0])
    gyro = np.array([0.0,0.0,0.0])

    delta_accel = np.array([0.0,0.0,0.0])
    delta_gyro = np.array([0.0,0.0,0.0])

    prev_gyro = np.array([0.0,0.0,0.0])
    prev_accel = np.array([0.0,0.0,0.0])

    velocity = np.array([0.0,0.0,0.0])

    position = np.array([0.0,0.0,0.0])
    rotate_position = np.array([0,0,0],dtype=np.float32)

    gravity_vector = np.array([0,0,0],dtype=np.float32)

    z = np.array([0.0,0.0,0.0]) #Weight in zindex - 1

    p = np.array([0.0,0.0,0.0]) #Proportional
    e = np.array([0.0,0.0,0.0]) #Exponential 
    
    ACCEL_THRESHOLD = np.array([2,2,2],dtype=np.float32)
    JERK_THRESHOLD = np.array([50,50,50])

    MOVE_VEL_THRESHOLD = np.array([2,2,2])
    ROTATE_VEL_THRESHOLD = np.array([0.01,0.01,0.04])

    timer = Timer()

    rotational_acceleration = False
    translational_acceleration = False

    rotational_movement = False
    translational_movement = False

    first_reading = True

    Q = np.array([100,100,100])


    accel_error = np.array([0,0,0],dtype=np.float32)

    start_time = time.perf_counter()

    current_config_sample = 0
    CONFIG_SAMPLES = 5
    

    LEFT = 0 #X
    DOWN = 1 #Y
    FORWARD = 2 #Z

    ROLL = 0
    PITCH = 1
    YAW = 2
    
    rotating = False
    ROTATING_KALMAN_THRESHOLD = 0.05

    jerk = False
    def calculate_gravity_vector():
        IMU.gravity_vector[IMU.FORWARD] = IMU.gravity * math.sin(IMU.rotate_position[IMU.PITCH])
        IMU.gravity_vector[IMU.LEFT] = (IMU.gravity * math.cos(IMU.rotate_position[IMU.PITCH]) * math.sin(IMU.rotate_position[IMU.ROLL]))
        IMU.gravity_vector[IMU.DOWN] = IMU.gravity * math.cos(IMU.rotate_position[IMU.PITCH]) * math.cos(IMU.rotate_position[IMU.ROLL])
        return IMU.gravity_vector
    def start():
        IMU.start_time = time.perf_counter()
        IMU.timer.reset()
        IMU.state = IMUState.CONFIG_ANGLE
    def predict(delta_time):
        #IMU.position += IMU.velocity * delta_time
        IMU.state_variance += (IMU.Q * delta_time)
    def update(measured_accel,raw_gyro,delta_time):
        raw_gyro[IMU.YAW] *= -1
        IMU.prev_accel = IMU.accel
        IMU.accel = measured_accel
        IMU.rotate_position += raw_gyro * delta_time

        """ K = IMU.state_variance / (IMU.state_variance + IMU.ACCEL_VARIANCE)
        IMU.accel += K * (measured_accel - IMU.accel)
        IMU.state_variance = (np.array([1,1,1]) - K) * (IMU.state_variance)"""

        #IMU.ACCEL_VARIANCE += IMU.ACCEL_VARIANCE * delta_time * 0.01
    def run(raw_accel, raw_gyro):

        if (raw_accel.any() == None):
            return
        if (raw_gyro.any() == None):
            return
        

        raw_accel = meters_to_inches(raw_accel)

        if (IMU.state == IMUState.DISABLED):
            return
        raw_accel -= IMU.gravity_vector
       # plt.scatter(time.perf_counter() - IMU.start_time,IMU.rotate_position[IMU.YAW],color = "red")
        #plt.scatter(time.perf_counter() - IMU.start_time,IMU.rotate_position[IMU.PITCH],color = "blue")
        #plt.scatter(time.perf_counter() - IMU.start_time,IMU.rotate_position[IMU.ROLL],color = "green")

        
        raw_accel -= IMU.accel_error

        delta_time = IMU.timer.time_passed()
        IMU.timer.reset()

        IMU.predict(delta_time)

        IMU.gyro = raw_gyro
        IMU.delta_gyro = IMU.gyro - IMU.prev_gyro
        IMU.prev_gyro = IMU.gyro
        IMU.rotating = False
        for i in range(len(IMU.ROTATE_VEL_THRESHOLD)):
            if (abs(IMU.delta_gyro[i]) > IMU.ROTATE_VEL_THRESHOLD[i]):
                IMU.rotating = True

        IMU.update(raw_accel,raw_gyro,delta_time)

        IMU.delta_accel = IMU.accel - IMU.prev_accel
        jerk = IMU.delta_accel / delta_time
        IMU.jerk = False
        for i in range(len(IMU.JERK_THRESHOLD)):
            if (abs(jerk[i]) > IMU.JERK_THRESHOLD[i]):
                IMU.jerk = True

        #plt.scatter(time.perf_counter() - IMU.start_time,jerk[0],color = "red")

        #plt.scatter(time.perf_counter() - IMU.start_time,raw_gyro[IMU.YAW],color = "red")
        for i in range(len(IMU.accel)):
            accel = IMU.accel[i]
            velocity = accel * delta_time
            IMU.velocity[i] += velocity
            IMU.position[i] += (IMU.velocity[i] * delta_time) + ((1/2) * (accel) * (delta_time ** 2))


        if (IMU.first_reading):
            IMU.first_reading = False
            IMU.position = np.array([0.0,0.0,0.0])
            IMU.velocity = np.array([0.0,0.0,0.0])
            IMU.predicted_accel = np.array([0.0,0.0,0.0])

      #  plt.scatter(time.perf_counter() - IMU.start_time,IMU.accel[IMU.FORWARD],color = "red")
      #  plt.scatter(time.perf_counter() - IMU.start_time,IMU.accel[IMU.DOWN],color = "blue")
      #  plt.scatter(time.perf_counter() - IMU.start_time,IMU.accel[IMU.LEFT],color = "green")

     #   plt.scatter(time.perf_counter() - IMU.start_time,IMU.velocity[IMU.FORWARD],color = "red")
     #   plt.scatter(time.perf_counter() - IMU.start_time,IMU.velocity[IMU.DOWN],color = "blue")
     #   plt.scatter(time.perf_counter() - IMU.start_time,IMU.velocity[IMU.LEFT],color = "green")

     #   plt.scatter(time.perf_counter() - IMU.start_time,IMU.position[IMU.FORWARD],color = "red")
     #   plt.scatter(time.perf_counter() - IMU.start_time,IMU.position[IMU.DOWN],color = "blue")
      #  plt.scatter(time.perf_counter() - IMU.start_time,IMU.position[IMU.LEFT],color = "green")

        #print(IMU.status())
        
        
    def status():
        stats = "---IMU---"
       # stats += f"\nTRANSLATE ACCELLERATING: {IMU.translational_acceleration}"
       # stats += f"\nROTATIONAL ACCELLERATING: {IMU.rotational_acceleration}"
       # stats += f"\nTRANSLATE MOVING: {IMU.translational_movement}"
       # stats += f"\nROTATIONAL MOVING: {IMU.rotational_movement}"

        stats += "\nACCEL: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.accel[i]} "
        stats += "\nGYRO: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.gyro[i]} "

        stats += "\nDELTA_ACCEL: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.delta_accel[i]} "
        

        stats += "\nVELOCITY: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.velocity[i]} "
        
        stats += "\nPOSITION: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.position[i]} "
        stats += "\nROTATE_POSITION: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.rotate_position[i]} "
        stats += "\nMODEL VARIANCE: "
        for i in range(3):
            stats += str(IMU.state_variance[i])
        return stats
        
    def i_to_axis(sensor,i):
        if (sensor == IMU.ROTATE):
            if (i == IMU.ROLL):
                return "ROLL"
            if (i == IMU.PITCH):
                return "PITCH"
            if (i == IMU.YAW):
                return "YAW"
        else:
            if (i == IMU.LEFT):
                return "X"
            if (i == IMU.DOWN):
                return "Y"
            if (i == IMU.FORWARD):
                return "Z"

class CompassKalman():
    yaw_variance = 1000
    gps_variance = 0.5

    Q = 0.1
    def predict():
        CompassKalman.yaw_variance += CompassKalman.Q
    def update():
        if (GPS.rover.cogd == None or GPS.rover.cogd == 0 or abs(IMU.gyro[IMU.YAW]) > (IMU.ROTATE_VEL_THRESHOLD[IMU.YAW])):
            return
        measure = math.radians(GPS.rover.cogd)
        if (measure > math.pi):
            measure -= 2 * math.pi
        #plt.scatter(time.perf_counter() - IMU.start_time,measure,color = "green")
        K = CompassKalman.yaw_variance / (CompassKalman.yaw_variance + CompassKalman.gps_variance)
        IMU.rotate_position[IMU.YAW] =   add_angle(IMU.rotate_position[IMU.YAW] * (1 - K), measure * (K))
        CompassKalman.yaw_variance = (1 - K) * CompassKalman.yaw_variance

class LocalizationKalman():
    GPS_POSE_NOISE = {}
    GPS_POSE_NOISE[FIX_STANDARD_GPS] = 200
    GPS_POSE_NOISE[FIX_DIFFERENTIAL_GPS] = 79
    GPS_POSE_NOISE[FIX_RTK_FLOAT] = 39
    GPS_POSE_NOISE[FIX_RTK_FIXED] = 15

    GPS_COG_NOISE = 0.1
    RTK_GPS_COG_NOISE = 0.05

    IMU_NOISE = 0.0001

    position_estimate_noise = 100
    yaw_esimate_noise = 100

    def predict():
        pass
    def update():
        pass

class Localizer():
    def get_raw_odo():
        results = send_command(f'{Device.Odometry.value},{Request.GET.value},{"0"}',read=True)
        if (results == None):
            return
        Label,_,results = results.partition(",")
        if (not Label == "ODOMETRY"):
            return
        x,_,results = results.partition(",")
        y,_,results = results.partition(",")
        yaw,_,results = results.partition(",")
        print(x,y,yaw)
        Localizer.y = float(y)
        Localizer.x = float(x)
        Localizer.yaw = float(yaw)
    def set_odo(x=None,y=None,yaw = 0):
        value = f"x:{x},y:{y},yaw:{yaw}"
        send_command(f'{Device.Odometry.value},{Request.SET.value},{value}')
    moving = False
    timer = Timer()

    x = 0
    y = 0
    yaw = 0

    target_x = 0
    target_y = 0
    target_yaw = 0

    def start():
        Camera.start()
        GPS.start()
        time.sleep(0.5)
        Localizer.timer.reset()
        plt.xlabel('Delta Time')
        plt.ylabel('eee')
        plt.title('Plot')
        Localizer.x = 0
        Localizer.y = 0
        Localizer.yaw = 0
        Localizer.target_x = 0
        Localizer.target_y = 0
        Localizer.target_yaw = 0
    def run():
        Camera.read()
        GPS.update()
        CompassKalman.predict()
        CompassKalman.update()
        Localizer.get_raw_odo()
    def status():
        return f"\n---LOCALIZER--\nYaw: {Localizer.yaw}\nTargetX: {Localizer.target_x}\nTargetY: {Localizer.target_y}\nTargetYaw: {Localizer.target_yaw} \
\n{Camera.status()}\n{GPS.status()}\n{IMU.status()}\n{Map.status()} "
    def show():
        plt.show()


if __name__ == "__main__":
    #GPS.start()
    Localizer.start()
    while Localizer.timer.time_passed() < 20:
        Localizer.run()
    Localizer.show()
