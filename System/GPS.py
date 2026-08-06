import math
import re
import time
from enum import Enum

import matplotlib.pyplot as plt
import serial

from timer import Timer


def recursive_average(prev,current,quantity):
        if (quantity <= 0):
            return current
        return prev + (current - prev)/quantity


def miles_to_inches(miles):
    return miles * 63360
def kilometers_per_hour_to_inches_per_second(kilometers):
    return kilometers * 10.936132983377


FIX_RTK_FIXED = 4
FIX_RTK_FLOAT = 5
FIX_STANDARD_GPS = 1
FIX_DIFFERENTIAL_GPS = 2

COG_DIFFERENTIAL_GPS = 'D'

class CoordinateSystem(Enum):
    DECIMAL_DEGREES_MINUTES = "DDMM.MMMMM" #What gps read
    DECIMAL_DEGREES = "DD" #Google maps
    LOCAL = "LOCAL"
    LONGITUDE = "LONGITUDE"
    LATITUDE = "LATITUDE"
    @staticmethod
    def DDM_TO_DD(ddm : str, coordinate_type = LATITUDE):
        #latitude: ddmm.mmmmm
        #longitude: dddmm.mmmmm
        #LAT: 3604.36674 LON: 07946.53373
        index = 2
        if not len(ddm) == 10 and coordinate_type == CoordinateSystem.LATITUDE:
            return
        if not len(ddm) == 11 and coordinate_type == CoordinateSystem.LONGITUDE:
            return
        if (coordinate_type == CoordinateSystem.LONGITUDE):
            index += 1
        dd = int(ddm[:index])
        m = ddm[index:]
        m = float(m)
        return (dd + (m / 60))
    @staticmethod
    def displacement(coordinates1,coordinates2):
        start_lat = coordinates2[0]
        start_lon = coordinates2[1]

        lat = coordinates1[0]
        lon = coordinates1[1]

        avg_lat = math.radians(CoordinateSystem.average_coordinates(lat,start_lat))

        delta_lat = (lat - start_lat) * 69.1
        delta_lon = (lon - start_lon) * 69.1 * math.cos(avg_lat)

        delta_lat = miles_to_inches(delta_lat)
        delta_lon = miles_to_inches(delta_lon)

        distance = math.sqrt((delta_lat ** 2) + (delta_lon ** 2))

        return delta_lat,delta_lon,distance
    @staticmethod
    def average_coordinates(c1,c2):
        return (c2 + c1) / 2
    @staticmethod
    def cumulative_average_coordinates(coordinates):
        avg = 0
        for coordinate in coordinates:
            coordinate = coordinate
            avg += coordinate
        avg /= len(coordinates)
        return avg
    @staticmethod
    def degrees_to_direction(angle : float):
        if angle < 0:
            angle += 360
        if angle > 360:
            angle -= 360
        #North is 0/360
        #West is 270
        #East is 90
        #South is 180
        increment = 30

        W = 270
        E = 90
        S = 180

        if (angle == 0.0):
            return "N/A"


        if (angle > 360 - increment or angle < 0 + increment):
            return "NORTH"
        if (angle > W - increment and angle < W + increment):
            return "WEST"
        if (angle > E - increment and angle < E + increment):
            return "EAST"
        if (angle > S - increment and angle < S + increment):
            return "SOUTH"
        if (angle < 360 - increment and angle > W - increment):
            return "NORTHWEST"
        if (angle < W + increment and angle > S - increment):
            return "SOUTHWEST"
        if (angle < S + increment and angle > E - increment):
            return "SOUTHEAST"
        if (angle < E - increment and angle > 0 + increment):
            return "NORTHEAST"





class GPSReceiver:
    POSITION_STREAM = '$GNGGA'
    VELOCITY_STREAM = '$GNVTG'

    ROVER = "ROVER"
    BASE = "BASE"

    NANO = "NANO"
    WINDOWS = "WINDOWS"

    BAUD_RATE = 115200

    RTK_STREAM = ''

    GPS_PORT = '/dev/gps'
    RADIO_PORT = '/dev/radio'

    def __init__(self,type):
        self.serial_port = GPSReceiver.GPS_PORT
        if (type == GPSReceiver.BASE):
            self.serial_port = GPSReceiver.RADIO_PORT
        self.type = type
        self.connected = False

        self.longitude : float = 0
        self.latitude : float = 0
        self.fix_quality : int = 0

        self.cogd = 0
        self.sogk = 0

        self.velocity = 0

        self.vel_quality = 'N'

        self.target_stream =self.POSITION_STREAM + self.VELOCITY_STREAM

    def start(self):
        self.connected = False
        try:
            self.serial = serial.Serial(self.serial_port,  self.BAUD_RATE, timeout=1)
            self.connected = True
            print(f"Connected to {self.type} RTK receiver via {self.serial_port}")
        except:
            print(f"Failed to connect to {self.serial_port} for {self.type} RTK receiver")
            return


    def read(self):
        if (self.type == self.BASE):
            return
        if (not  self.connected):
            print(f"{self.type} NOT CONNECTED")
            return
        lines = ''
        try:
            lines = self.serial.read_all().decode('utf-8', errors='ignore').strip()
        except:
            print("gps read failed")
            return
        lines = re.split(r'(\n)',lines)
        for line in (lines):
            if line.startswith(self.POSITION_STREAM):
                print(line)
                lat,lon,quality = GPSReceiver.parse_gps(line)
                if (lat == None or lon == None or lat == "" or lon == ""):
                    return
                lat = CoordinateSystem.DDM_TO_DD(lat,CoordinateSystem.LATITUDE)
                lon = CoordinateSystem.DDM_TO_DD(lon,CoordinateSystem.LONGITUDE)
                print(lat,lon)
                if (lat == self.latitude):
                    return
                if (lon == self.longitude):
                    return
                try:
                    self.start_position_found = True
                    self.latitude = float(lat)
                    self.longitude = -float(lon)
                    self.fix_quality = int(quality)
                except:
                    print("gps read failed")
                    return
            if line.startswith(self.VELOCITY_STREAM):
                cogd,sogk,quality = GPSReceiver.parse_gps(line)
                if (cogd == None or cogd == ""):
                    cogd = 0.0
                else:
                    cogd = float(cogd)
                self.cogd = cogd
                try:
                    self.sogk = float(sogk)
                    self.sogk = kilometers_per_hour_to_inches_per_second(self.sogk)
                except:
                    self.sogk = 0
                self.velocity = [self.sogk * math.cos(math.radians(self.cogd)),self.sogk * math.sin(math.radians(self.cogd))]
                self.vel_quality = quality

                for i in range(len(GPS.prev_angles)):
                    if (i == len(GPS.prev_angles) - 1):
                        GPS.prev_angles[i] = self.cogd
                    else:
                        GPS.prev_angles[i] = GPS.prev_angles[i + 1]


    def close(self):
        if (self.connected):
            self.serial.close()
        self.connected = False

    def status(self):
        if (self.type == self.BASE):
            return f"\n{self.type} connected:{self.connected} \n"
        return f"\n{self.type} connected:{self.connected}\nlatitude:{self.latitude}\nlongitude:{self.longitude}\nquality:{self.fix_quality}-{GPSReceiver.int_to_quality(self.fix_quality)}\n\
SPEED: {self.sogk}\nANGLE: {self.cogd}\nVEL_QUALITY: {self.vel_quality}\n\
DIRECTION: {CoordinateSystem.degrees_to_direction(self.cogd)}"

    @staticmethod
    def int_to_quality(quality):
        if (isinstance(quality,str)):
            quality = int(quality)
        if (quality == 1):
            return "Standard GPS" #1 - 5 m
        if (quality == 2):
            return "Differential GPS" #1 - 3m
        if (quality == 3):
            return "PPS" #Government signal, should not be possible
        if (quality == 4):
            return "RTK Fixed" #Most accurate 1 - 2 cm
        if (quality == 5):
            return "RTK Float" #20 - 50cm
        return "Invalid"

    @staticmethod
    def parse_gps(line :str):
        latitude = None
        longitude = None
        type,_,line = line.partition(f',')
        if (type == GPSReceiver.POSITION_STREAM):
            time,_,line = line.partition(",")
            latitude,_,line = line.partition(",")
            north_south,_,line = line.partition(",")
            longitude,_,line = line.partition(",")
            east_west,_,line = line.partition(",")
            fix_quality,_,line = line.partition(",")

            """
            print("TYPE",type)
            print("TIME: ", time)
            print("LATITIUDE: ",latitude)
            print("N/S: ",north_south)
            print("LONGITUDE: ",longitude)
            print("E/W: ",east_west)
            print("FIX QUALITY: ",fix_quality)
            """

            return latitude,longitude,fix_quality
        if (type == GPSReceiver.VELOCITY_STREAM):
            #print(line)
            course_over_ground_degrees,_,line = line.partition(",")
            _,_,line = line.partition(",")
            magnetic_heading_degrees,_,line = line.partition(",")
            _,_,line = line.partition(",")
            speed_knots,_,line = line.partition(",")
            _,_,line = line.partition(",")
            speed_km,_,line = line.partition(",")
            _,_,line = line.partition(",")
            fix_quality,_,line = line.partition("*")
            """
            print("course_over_ground_degrees: ",course_over_ground_degrees)
            print("magnetic_heading_degrees: ",magnetic_heading_degrees)
            print("speed_km: ",speed_km)
            print("fix_quality: ",fix_quality)
            """
            return course_over_ground_degrees,speed_km,fix_quality
class GPS:
    rover = GPSReceiver(GPSReceiver.ROVER)
    base = GPSReceiver(GPSReceiver.BASE)


    PERIOD = 0.1 #Time inbetween readings
    timer = Timer()


    start_time = time.perf_counter()

    local_grid = [0,0]

    start_coordinates = [0,0]

    started = False

    prev_angles = [0,0,0]
    prev_speeds = [0,0,0,0,0,0,0,0]

    speed_threshold = 4
    @staticmethod
    def get_data():
        return f"{GPS.rover.latitude},{GPS.rover.longitude}"
    @staticmethod
    def start():
        GPS.rover.start()
        GPS.base.start()
        #GPS.calculate_start_pos()
    @staticmethod
    def close():
        GPS.rover.close()
        GPS.base.close()
    @staticmethod
    def status():
        return "\n---GPS---\n"+ GPS.rover.status()+\
        GPS.base.status() + f"\n\
Local Grid: x: {GPS.local_grid[0]} y: {GPS.local_grid[1]}\n\
Start Coords: lat: {GPS.start_coordinates[0]} lon: {GPS.start_coordinates[1]}"
    @staticmethod
    def signal_base_to_rover():
        #TODO TEST RADIO
        return

        waiting = GPS.base.serial.in_waiting
        if waiting:
            data = GPS.base.serial.read(waiting)
            print("base wrote to rover")
            GPS.rover.serial.write(data)
            GPS.rover.serial.flush()

    @staticmethod
    def calculate_start_pos():
        GPS.started = False
        if not GPS.rover.connected:
            return
        while GPS.start_coordinates[0] == 0 and GPS.rover.connected:
            GPS.update()
            GPS.start_coordinates[0] = GPS.rover.latitude
            GPS.start_coordinates[1] = GPS.rover.longitude
        GPS.started = True
    @staticmethod
    def update():
       # print(GPS.status())
        if (GPS.rover.connected and GPS.base.connected):
            GPS.signal_base_to_rover()
        if (GPS.rover.connected):
            GPS.rover.read()
        if (GPS.started):
            d_lat,d_lon,distance = CoordinateSystem.displacement([GPS.rover.latitude,GPS.rover.longitude],GPS.start_coordinates)
            GPS.local_grid = [d_lat,d_lon]





#To run:
#Linux: python3 -m System.GPS
if __name__ == "__main__":
    GPS.start()
    while time.perf_counter() - GPS.start_time < 20:
        GPS.update()
    plt.show()
