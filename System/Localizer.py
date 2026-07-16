from timer import *
import math
import matplotlib.pyplot as plt
from enum import Enum
from System.GPS import *
from System.Camera import Camera,IMU,IMUState
import numpy as np

from pathlib import Path
from System.hardware import *
from System.mapping import *
from System.Constants import *
import time

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
    GYRO_VARIANCE_GAIN = 0.01
    ODOMETRY_VARIANCE_GAIN = 0.01
    Q = 0.001

    odo_variance = 0.1

    timer = Timer()

    delta_yaw_measured = 0

    def predict():
        delta_time = LocalizationKalman.timer.time_passed()
        delta_x,delta_y,delta_yaw = Localizer.get_raw_odo()
        distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
        
        delta_yaw = LocalizationKalman.gyro_odo_fusion(odo_delta_yaw = delta_yaw,
                                                       gyro_delta_yaw=Camera.raw_gyro_reading[IMU.YAW] * delta_time)
        Localizer.yaw += delta_yaw
        Localizer.yaw = angle_wrap(Localizer.yaw)
        Localizer.x += distance * math.cos(Localizer.yaw)
        Localizer.y += distance * math.sin(Localizer.yaw)

        LocalizationKalman.gyro_variance += (delta_time * LocalizationKalman.GYRO_VARIANCE_GAIN) + LocalizationKalman.Q
        LocalizationKalman.odo_variance += (delta_time * LocalizationKalman.ODOMETRY_VARIANCE_GAIN * distance) + LocalizationKalman.Q

        LocalizationKalman.timer.reset()
    def gyro_odo_fusion(odo_delta_yaw,gyro_delta_yaw):
        K = (LocalizationKalman.odo_variance) / (LocalizationKalman.odo_variance + LocalizationKalman.gyro_variance)
        odo_delta_yaw += K * (odo_delta_yaw - gyro_delta_yaw)
        LocalizationKalman.odo_variance = (1 - K) * LocalizationKalman.odo_variance
        return odo_delta_yaw
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
        return x,y,yaw
    moving = False
    timer = Timer()

    x = 0
    y = 0
    yaw = 0

    target_x = 0
    target_y = 0
    target_yaw = 0

    def rotating_fast():
        return abs(Camera.raw_gyro_reading[IMU.YAW] ) > 1

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
        #CompassKalman.predict()
        #CompassKalman.update()
        LocalizationKalman.predict()
        LocalizationKalman.update()

        #TODO Replace with map update method
        Map.update(Localizer.x,Localizer.y,Localizer.yaw,Camera.closest,Localizer.rotating_fast())

    def status():
        return f"\n---LOCALIZER--\nYaw: {Localizer.yaw}\nTargetX: {Localizer.target_x}\nTargetY: {Localizer.target_y}\nTargetYaw: {Localizer.target_yaw} \
\n{Camera.status()}\n{GPS.status()}\n{Map.status()} "
    def show():
        plt.show()

#python -m System.Camera
if __name__ == "__main__":
    #GPS.start()
    Localizer.start()
    while Localizer.timer.time_passed() < 20:
        Localizer.run()
    Localizer.show()
