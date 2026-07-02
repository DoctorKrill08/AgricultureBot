from timer import Timer
def meters_to_inches(meters):
    return meters * 39.3701
import numpy as np
import math

class IMU():

    def add_angle(a,b):
        return a + b

    POSITION = 0
    ROTATE = 1

    gravity = -386.089 #Inches per second^2

    NOISE_ACCEL_CONSTANTS = np.array([0,gravity,0]) 
    
    noise_accel = np.array([0,0,0]) 

    accel = np.array([0.0,0.0,0.0])
    gyro = np.array([0.0,0.0,0.0])

    delta_accel = np.array([0.0,0.0,0.0])
    delta_gyro = np.array([0.0,0.0,0.0])

    predicted_accel = np.array([0.0,0.0,0.0])
    predicted_gyro = np.array([0.0,0.0,0.0])

    prev_gyro = np.array([0.0,0.0,0.0])
    prev_accel = np.array([0.0,0.0,0.0])

    velocity = np.array([0.0,0.0,0.0])

    position = np.array([0.0,0.0,0.0])
    rotate_position = np.array([math.radians(0),math.radians(1.55),0.0])

    z = np.array([0.0,0.0,0.0]) #Weight in zindex - 1

    p = np.array([0.0,0.0,0.0]) #Proportional
    e = np.array([0.0,0.0,0.0]) #Exponential 
    
    MOVE_ACCEL_THRESHOLD = np.array([2,2,2])

    MOVE_VEL_THRESHOLD = np.array([0.0,0.0,0.0])
    ROTATE_VEL_THRESHOLD = np.array([0.0,0.0,0.0])




    timer = Timer()

    rotational_acceleration = False
    translational_acceleration = False

    rotational_movement = False
    translational_movement = False

    def calculate_noise():
        roll,pitch,yaw = IMU.rotate_position
        print('r: ',roll,' p: ',pitch, ' y: ',yaw)
        IMU.noise_accel =  np.array([-IMU.gravity * math.sin(pitch),IMU.gravity * math.sin(roll) * math.cos(pitch),IMU.gravity * math.cos(roll) * math.cos(pitch)])
        print('noise x: ',IMU.noise_accel[0])
        print('noise y: ',IMU.noise_accel[1])
        print('noise z: ',IMU.noise_accel[2])
    def filter(raw_accel,raw_gyro):
        predicted_accel = raw_accel- IMU.noise_accel
        delta_accel = raw_accel - IMU.prev_gyro
        IMU.translational_acceleration = False
        abs_p_accel = np.abs(predicted_accel)
        if (abs_p_accel[0] > IMU.MOVE_ACCEL_THRESHOLD[0] and abs_p_accel[1] > IMU.MOVE_ACCEL_THRESHOLD[1]):
            IMU.translational_acceleration = True
        if (IMU.translational_acceleration):
            IMU.accel = raw_accel
            IMU.predicted_accel = predicted_accel
        
        IMU.gyro = raw_gyro

    def predict(delta_time):
        IMU.velocity += (IMU.predicted_accel * delta_time)
        IMU.position += (IMU.velocity * delta_time) + (1/2) * (IMU.predicted_accel *  (delta_time ** 2))
        
        IMU.rotate_position += (
            IMU.prev_gyro + IMU.gyro
        ) * 0.5 * delta_time

        IMU.prev_gyro = IMU.gyro
        IMU.prev_accel = IMU.accel
        




    def start():
        IMU.timer.reset()
        pass
    def read(raw_accel, raw_gyro):

        if (raw_accel.any() == None or raw_accel.any() == 0.0):
            return
        if (raw_gyro.any() == None or raw_gyro.any() == 0.0):
            return

        IMU.calculate_noise()

        IMU.filter(raw_accel,raw_gyro)

        delta_time = IMU.timer.time_passed()
        IMU.timer.reset()


        IMU.translational_acceleration = False
        IMU.rotational_acceleration = False

        IMU.predict(delta_time)
        print(IMU.status())
        
        



        

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
        

        stats += "\nPREDICTED_ACCEL: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.predicted_accel[i]} "
        stats += "\nPREDICTED_GYRO: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.predicted_gyro[i]} "

        stats += "\nDELTA_ACCEL: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.delta_accel[i]} "
        stats += "\nDELTA_GYRO: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.delta_gyro[i]} "
        

        stats += "\nVELOCITY: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.velocity[i]} "
        
        stats += "\nPOSITION: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.POSITION,i)}: {IMU.position[i]} "
        stats += "\nROTATE_POSITION: "
        for i in range(3):
            stats += f"{IMU.i_to_axis(IMU.ROTATE,i)}: {IMU.rotate_position[i]} "

        return stats
        
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