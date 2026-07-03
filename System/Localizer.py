from timer import *
def meters_to_inches(meters):
    return meters * 39.3700787402
import numpy as np
import math
import matplotlib.pyplot as plt
from enum import Enum
from System.GPS import *

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
    
    MOVE_ACCEL_THRESHOLD = np.array([0.5,0.5,0.5])

    MOVE_VEL_THRESHOLD = np.array([2,2,2])
    ROTATE_VEL_THRESHOLD = np.array([0.0,0.0,0.0])

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

    def config_angle(accel):
        IMU.accel = recursive_average(IMU.accel,accel,IMU.current_config_sample)
        IMU.current_config_sample += 1

        IMU.rotate_position[IMU.PITCH] = math.atan2(IMU.accel[IMU.FORWARD],IMU.accel[IMU.DOWN])
        IMU.rotate_position[IMU.ROLL] = math.asin(max(min(IMU.accel[IMU.LEFT],-1),1) / IMU.gravity)
        IMU.rotate_position[IMU.YAW] = 0.0



        print("CONFIGING_ANGLE: ",IMU.rotate_position)
        if (IMU.current_config_sample > IMU.CONFIG_SAMPLES):
            IMU.current_config_sample = 0
            IMU.state = IMUState.CONFIG_ERROR
    def config_error(accel):
        IMU.accel_error = recursive_average(IMU.accel_error,accel,IMU.current_config_sample)
        IMU.current_config_sample += 1
        print("CONFIGING_ERROR: ",IMU.rotate_position)
        if (IMU.current_config_sample > IMU.CONFIG_SAMPLES):
            IMU.current_config_sample = 0
            IMU.state = IMUState.ACTIVE
    def calculate_gravity_vector():
        IMU.gravity_vector[IMU.FORWARD] = IMU.gravity * math.sin(IMU.rotate_position[IMU.PITCH])
        IMU.gravity_vector[IMU.LEFT] = (IMU.gravity * math.cos(IMU.rotate_position[IMU.PITCH]) * math.sin(IMU.rotate_position[IMU.ROLL]))
        IMU.gravity_vector[IMU.DOWN] = IMU.gravity * math.cos(IMU.rotate_position[IMU.PITCH]) * math.cos(IMU.rotate_position[IMU.ROLL])
        return IMU.gravity_vector
    def show():
        plt.show()

    def start():
        IMU.start_time = time.perf_counter()
        IMU.timer.reset()
        plt.xlabel('Delta Time')
        plt.ylabel('Acceleration')
        plt.title('Aceeleration Plot')
        IMU.state = IMUState.CONFIG_ANGLE
    def predict(delta_time):
        #IMU.position += IMU.velocity * delta_time
        IMU.state_variance += (IMU.Q * delta_time)
    def update(measured_accel,raw_gyro,delta_time):
        IMU.prev_gyro = IMU.gyro
        IMU.gyro = raw_gyro

        IMU.rotate_position += (IMU.gyro + IMU.prev_gyro) * 0.5 * delta_time

        IMU.prev_accel = measured_accel

        K = IMU.state_variance / (IMU.state_variance + IMU.ACCEL_VARIANCE)
        IMU.accel += K * (measured_accel - IMU.accel)
        IMU.state_variance = (np.array([1,1,1]) - K) * (IMU.state_variance)

        #IMU.ACCEL_VARIANCE += IMU.ACCEL_VARIANCE * delta_time * 0.01
    def run(raw_accel, raw_gyro):

        if (raw_accel.any() == None):
            return
        if (raw_gyro.any() == None):
            return
        

        raw_accel = meters_to_inches(raw_accel)
        print("Raw: ", raw_accel)

        if (IMU.state == IMUState.DISABLED):
            return
        
        plt.scatter(time.perf_counter() - IMU.start_time,IMU.rotate_position[IMU.YAW],color = "red")
        #plt.scatter(time.perf_counter() - IMU.start_time,IMU.rotate_position[IMU.PITCH],color = "blue")
        #plt.scatter(time.perf_counter() - IMU.start_time,IMU.rotate_position[IMU.ROLL],color = "green")

        if (IMU.state == IMUState.CONFIG_ANGLE):
            IMU.config_angle(raw_accel)
            return
        raw_accel -= IMU.calculate_gravity_vector()
        if (IMU.state == IMUState.CONFIG_ERROR):
            IMU.config_error(raw_accel)
            return
       # plt.scatter(time.perf_counter() - IMU.start_time,IMU.accel[IMU.FORWARD],color = "red")
        #plt.scatter(time.perf_counter() - IMU.start_time,IMU.accel[IMU.DOWN],color = "blue")
       # plt.scatter(time.perf_counter() - IMU.start_time,IMU.accel[IMU.LEFT],color = "green")
        raw_accel -= IMU.accel_error
        print("grav: ", IMU.gravity_vector)

        delta_time = IMU.timer.time_passed()
        IMU.timer.reset()

        IMU.predict(delta_time)


        IMU.update(raw_accel,raw_gyro,delta_time)



        IMU.translational_acceleration = False
        IMU.rotational_acceleration = False


        if (IMU.first_reading):
            IMU.first_reading = False
            IMU.position = np.array([0.0,0.0,0.0])
            IMU.velocity = np.array([0.0,0.0,0.0])
            IMU.predicted_accel = np.array([0.0,0.0,0.0])

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





class Localizer:
    LAT = 0
    LONG = 1
    COGD = 2

    X = 0
    Y = 1
    YAW = 2
    local_grid = np.array([0,0,0],dtype=np.float32)

    global_grid = np.array([0,0,0])

    def run():
        pass
