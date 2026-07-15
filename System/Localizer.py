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
        Localizer.yaw =float(yaw)
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
        Localizer.yaw = IMU.rotate_position[IMU.YAW]

        #TODO Replace with map update method
        Map.update(Localizer.x,Localizer.y,Localizer.yaw,Camera.closest,IMU.rotating_fast())

    def status():
        return f"\n---LOCALIZER--\nYaw: {Localizer.yaw}\nTargetX: {Localizer.target_x}\nTargetY: {Localizer.target_y}\nTargetYaw: {Localizer.target_yaw} \
\n{Camera.status()}\n{GPS.status()}\n{IMU.status()}\n{Map.status()} "
    def show():
        plt.show()

#python -m System.Camera
if __name__ == "__main__":
    #GPS.start()
    Localizer.start()
    while Localizer.timer.time_passed() < 20:
        Localizer.run()
    Localizer.show()
