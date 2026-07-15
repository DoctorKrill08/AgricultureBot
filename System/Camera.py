import numpy as np
import os
import sys
from System.Constants import *
from timer import *
from enum import Enum
import cv2

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
    WIDTH_RANGE = CENTER_X - 40
    MIN_HEIGHT = HEIGHT - 30
    MAX_HEIGHT = 30
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

    prev_frame = None
    canvas = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)

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
        return f"\n-----CAMERA-----\nCamera on: {Camera.on}\nTOO CLOSE: {Camera.too_close}"
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
            IMU.start()
            print("IMU CONNECTED")
        except Exception as e:
            Camera.IMU_enabled = False
            Camera.exception()
            print("IMU NOT CONNECTED", e)

        try:
            #vision_cfg.enable_stream(rs.stream.color, Camera.WIDTH,Camera.HEIGHT, rs.format.bgr8, Camera.FPS)
            vision_cfg.enable_stream(rs.stream.depth, Camera.WIDTH,Camera.HEIGHT, rs.format.z16, Camera.FPS)
            Camera.vision_pipe.start(vision_cfg)
            Camera.on = True
            print("CAMERA CONNECTED")
        except Exception as e:
            Camera.on = False
            Camera.exception()
            print("CAMERA NOT CONNECTED", e)

        

    def read():
        if (not Camera.on):
            return
        
        frame = Camera.vision_pipe.wait_for_frames()
        depth_frame = frame.get_depth_frame()
        #color_frame = frame.get_color_frame()

        depth_image = np.asanyarray(depth_frame.get_data())
        #color_image = np.asanyarray(color_frame.get_data())
        #depth_cm = cv2.applyColorMap(cv2.convertScaleAbs(depth_image,alpha = 0.03), cv2.COLORMAP_JET)
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
    def blacklist(x,y,blacklist_array):
        key = str(x) + "," + str(y)
        blacklist_array[key] = [x,y]
        return blacklist_array
    def paint_on_canvas(canvas,x,y,size,color = [0,0,255]):
        canvas[y-(size):y+(size), x-(size):x+(size)] = color
        return canvas
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
                if (z <= CAMERA_MIN_DEPTH or z > CAMERA_MAX_DEPTH or prev_z <= CAMERA_MIN_DEPTH or prev_z > CAMERA_MAX_DEPTH):
                    blacklist_image = Camera.paint_on_canvas(blacklist_image,x,y,Camera.SPACE_BETWEEN_RAYS,[0,255,255])
                    blacklisted_pixels = Camera.blacklist(x,y,blacklisted_pixels)
                    continue
                delta_z = z - prev_z
                if (abs(delta_z) > 2):
                    blacklist_image = Camera.paint_on_canvas(blacklist_image,x,y,Camera.SPACE_BETWEEN_RAYS,[0,0,255])
                    blacklisted_pixels = Camera.blacklist(x,y,blacklisted_pixels)
                    continue
        Camera.prev_frame = depth_frame
        return blacklisted_pixels,blacklist_image
    def closest_pixels_1D(depth_frame,blacklisted_pixels = None):
        depth_intrin = depth_frame.profile.as_video_stream_profile().get_intrinsics()
        closest_y = 1000
        #Forward,Horizontal
        points_1D = [None] * Camera.WIDTH
        for x in range(Camera.CENTER_X - Camera.WIDTH_RANGE, Camera.CENTER_X + Camera.WIDTH_RANGE, Camera.SPACE_BETWEEN_RAYS):
            closest_y = 1000
            for y in range(Camera.MAX_HEIGHT,Camera.MIN_HEIGHT, Camera.SPACE_BETWEEN_RAYS): 
                if (not blacklisted_pixels == None):
                    key = str(x) + "," + str(y)
                    if not blacklisted_pixels[key] == None:
                        continue
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

        IMU.update(raw_accel,raw_gyro,delta_time)

        #plt.scatter(time.perf_counter() - IMU.start_time,jerk[0],color = "red")

        #plt.scatter(time.perf_counter() - IMU.start_time,raw_gyro[IMU.YAW],color = "red")


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
            
#Windows: python -m System.Camera
if __name__ == "__main__":
    Camera.start()
    while True:
        Camera.read()
        if cv2.waitKey(1) == ord('q'):
            break
    Camera.stop()