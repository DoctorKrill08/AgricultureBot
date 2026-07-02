from System.Camera import *
from timer import Timer
import numpy as np

class IMU():

    def add_angle(a,b):
        return a + b

    POSITION = 0
    ROTATE = 1

    gravity = 386.089 #Inches per second^2

    NOISE = np.array([0,0,0]) 


    accel = np.array([0,0,0])
    gyro = np.array([0,0,0])

    prev_accel = np.array([0,0,0])
    prev_gyro = np.array([0,0,0])

    delta_accel = np.array([0,0,0])
    delta_gyro = np.array([0,0,0])

    velocity = np.array([0,0,0])
    rotate_velocity = np.array([0,0,0])

    position = np.array([0,0,0])
    rotate_position = np.array([0,0,0])

    z = np.array([0,0,0]) #Weight in zindex - 1

    p = np.array([0,0,0]) #Proportional
    e = np.array([0,0,0]) #Exponential 
    
    MOVE_ACCEL_THRESHOLD = np.array([0,0,0])
    ROTATE_ACCEL_THRESHOLD = np.array([0,0,0])

    MOVE_VEL_THRESHOLD = np.array([0,0,0])
    ROTATE_VEL_THRESHOLD = np.array([0,0,0])




    timer = Timer()

    rotational_acceleration = False
    translational_acceleration = False

    rotational_movement = False
    translational_movement = False

    

    def start():
        IMU.timer.reset()
        pass
    def read():
        IMU.prev_accel = IMU.accel
        IMU.prev_gyro = IMU.gyro

        #IMU.accel = ...
        IMU.delta_accel = IMU.accel - IMU.prev_accel
        IMU.delta_gyro = IMU.gyro - IMU.prev_gyro

        delta_time = IMU.timer.time_passed()
        IMU.timer.reset()

        d_accel = np.abs(IMU.delta_accel)
        d_gyro = np.abs(IMU.delta_gyro)

        IMU.translational_acceleration = False
        IMU.rotational_acceleration = False

        for i in range(len(d_accel)):
            if (d_accel[i] > IMU.MOVE_ACCEL_THRESHOLD[i]):
                IMU.translational_acceleration = True

        for i in range(len(d_gyro)):
            if (d_gyro[i] > IMU.ROTATE_ACCEL_THRESHOLD[i]):
                IMU.rotational_acceleration = True
        
        if (IMU.translational_acceleration):
            delta_v = d_accel * delta_time
            IMU.velocity += delta_v
        
        if (IMU.rotational_acceleration and IMU.translational_acceleration):
            delta_v = d_gyro * delta_time
            IMU.rotate_velocity += delta_v
        
        for i in range(len(IMU.velocity)):
            if (IMU.velocity[i] > IMU.MOVE_VEL_THRESHOLD[i]):
                IMU.translational_movement = True

        for i in range(len(IMU.velocity)):
            if (IMU.rotate_velocity[i] > IMU.ROTATE_VEL_THRESHOLD[i] and IMU.translational_movement):
                IMU.rotational_movement = True
        
        if (IMU.translational_acceleration):
            delta_p = IMU.velocity * delta_time
            IMU.position += delta_p
        
        if (IMU.rotational_movement and IMU.translational_movement):
            delta_p = IMU.rotate_velocity * delta_time
            IMU.rotate_position += delta_p



        

    def status():
        stats = "---IMU---"
        stats += f"\nTRANSLATE ACCELLERATING: {IMU.translational_acceleration}"
        stats += f"\nROTATIONAL ACCELLERATING: {IMU.rotational_acceleration}"
        stats += f"\nTRANSLATE MOVING: {IMU.translational_movement}"
        stats += f"\nROTATIONAL MOVING: {IMU.rotational_movement}"

        stats += "\nACCEL: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.accel[i]}"
        stats += "\nGYRO: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.gyro[i]}"
        

        stats += "\nDELTA_ACCEL: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.delta_accel[i]}"
        stats += "\nDELTA_GYRO: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.delta_gyro[i]}"
        

        stats += "\nVELOCITY: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.velocity[i]}"
        stats += "\ROTATE_VELOCITY: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.rotate_velocity[i]}"
        
        stats += "\nPOSITION: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.position[i]}"
        stats += "\nROTATE_POSITION: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.rotate_position[i]}"
        
    def i_to_axis(sensor,i):
        if (sensor == IMU.ROTATE):
            if (i == 0):
                return "ROLL"
            if (i == 1):
                return "PITCH"
            if (i == 2):
                return "YAW"
        else:
            if (i == 0):
                return "X"
            if (i == 1):
                return "Y"
            if (i == 2):
                return "Z"





class Localizer:
    pass