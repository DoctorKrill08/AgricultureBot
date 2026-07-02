from System.Camera import *
from timer import Timer
import numpy as np

class IMU():
    POSITION = 0
    ROTATE = 1

    gravity = 386.089 #Inches per second^2

    DRIFT = np.array([0,0,0]) 


    accel = np.array([0,0,0])
    gyro = np.array([0,0,0])

    prev_accel = np.array([0,0,0])
    prev_gyro = np.array([0,0,0])

    delta_accel = np.array([0,0,0])
    delta_gyro = np.array([0,0,0])

    velocity = np.array([0,0,0])
    rotate_velocity = np.array([0,0,0])

    z = np.array([0,0,0]) #Weight in zindex - 1

    p = np.array([0,0,0]) #Proportional
    e = np.array([0,0,0]) #Exponential 
    
    MOVE_THRESHOLD = np.array([0,0,0])
    ROTATE_THRESHOLD = np.array([0,0,0])


    timer = Timer()

    rotating = False
    moving = False

    

    def start():
        IMU.timer.reset()
        pass
    def read():
        IMU.prev_accel = IMU.accel
        IMU.prev_gyro = IMU.gyro

        #IMU.accel = ...
        IMU.delta_accel = IMU.accel - IMU.prev_accel
        IMU.delta_gyro = IMU.gyro - IMU.prev_gyro

        d_accel = np.abs(IMU.delta_accel)
        d_gyro = np.abs(IMU.delta_gyro)

        IMU.moving = False
        IMU.rotating = False

        for i in range(len(d_accel)):
            if (d_accel[i] > IMU.MOVE_THRESHOLD[i]):
                IMU.moving = True

        for i in range(len(d_gyro)):
            if (d_gyro[i] > IMU.ROTATE_THRESHOLD[i]):
                IMU.rotating = True

        

    def status():
        stats = "---IMU---"
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
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.velocity[i]}"
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
