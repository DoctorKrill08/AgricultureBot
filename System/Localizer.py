import math
import time
from enum import Enum
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from System.Camera import IMU, Camera
from System.Constants import *
from System.GPS import *
from System.hardware import *
from System.Lidar import Lidar
from System.mapping import *
from System.Pathing import *
from timer import *


class LocalizationKalman:
    GYRO_VARIANCE = 0.01
    ODOMETRY_VARIANCE_GAIN = 0.01
    Q = 0.001

    odo_variance = 0.1

    timer = Timer()

    delta_yaw_measured = 0

    @staticmethod
    def predict():
        delta_time = LocalizationKalman.timer.time_passed()
        delta_x,delta_y,delta_yaw = Localizer.get_raw_odo()

        distance = math.sqrt((delta_x ** 2) + (delta_y ** 2))
        Localizer.estimated_speed = distance / delta_time

        LocalizationKalman.odo_variance += (delta_time * LocalizationKalman.ODOMETRY_VARIANCE_GAIN * distance) + LocalizationKalman.Q

        gyro_delta_yaw = Camera.raw_gyro_reading[IMU.YAW] * delta_time

        if (not Arduino.connected):
            delta_yaw = gyro_delta_yaw
        else:
            if (Camera.on):
                delta_yaw = LocalizationKalman.gyro_odo_fusion(odo_delta_yaw = delta_yaw,
                                                         gyro_delta_yaw=gyro_delta_yaw)

        Localizer.estimated_rotational_velocity = delta_yaw / delta_time

        look_at_angle = math.atan2(delta_y,delta_x)
        position_angle = angle_wrap(look_at_angle + Localizer.yaw)
        Localizer.x += distance * math.cos(position_angle)
        Localizer.y += distance * math.sin(position_angle)

        Localizer.yaw += delta_yaw
        Localizer.yaw = angle_wrap(Localizer.yaw)

        LocalizationKalman.timer.reset()
    @staticmethod
    def gyro_odo_fusion(odo_delta_yaw : float,gyro_delta_yaw : float) -> float:
        K = (LocalizationKalman.odo_variance) / (LocalizationKalman.odo_variance + LocalizationKalman.GYRO_VARIANCE)
        odo_delta_yaw +=(K * (gyro_delta_yaw - odo_delta_yaw))
        LocalizationKalman.odo_variance = (1 - K) * LocalizationKalman.odo_variance
        return odo_delta_yaw
class Localizer:
    @staticmethod
    def get_raw_odo():
        results = Arduino.send_command(f'{Device.Odometry.value},{"0"}',read=True)
        if (results == None):
            return 0,0,0
        Label,_,results = results.partition(",")
        if (Label != "ODOMETRY"):
            return 0,0,0
        x,_,results = results.partition(",")
        y,_,results = results.partition(",")
        yaw,_,results = results.partition(",")
        return float(x),float(y),float(yaw)
    moving = False
    timer = Timer()

    x : float = 0
    y : float = 0
    yaw : float = 0

    target_x : float = 0
    target_y : float = 0
    target_yaw : float = 0

    estimated_rotational_velocity : float = 0
    estimated_speed : float = 0
    @staticmethod
    def rotating_fast():
        return abs(Camera.raw_gyro_reading[IMU.YAW] ) > 1 or abs(Localizer.estimated_rotational_velocity) > 1.5

    @staticmethod
    def moving_fast():
        return Localizer.estimated_speed > 6

    @staticmethod
    def start():
        Camera.start()
        GPS.start()
        Lidar.start()
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
    @staticmethod
    def run():
        Camera.update()
        GPS.update()
        Lidar.calculate(Localizer.x,Localizer.y,Localizer.yaw)
        LocalizationKalman.predict()
        if (not Localizer.rotating_fast()):
            Map.update(Localizer.x,Localizer.y,Localizer.yaw,Lidar.obstacles,Camera.closest,abs(Localizer.estimated_rotational_velocity))
    @staticmethod
    def status():
        return f"\n---LOCALIZER--\nYaw: {Localizer.yaw}\nTargetX: {Localizer.target_x}\nTargetY: {Localizer.target_y}\nTargetYaw: {Localizer.target_yaw} \
\n{Camera.status()}\n{GPS.status()}\n{Lidar.status()}\n{Map.status()}\n{Pathing.status()} "

    @staticmethod
    def show():
        plt.show()

#python -m System.Camera
if __name__ == "__main__":
    #GPS.start()
    Localizer.start()
    while Localizer.timer.time_passed() < 20:
        Localizer.run()
    Localizer.show()
