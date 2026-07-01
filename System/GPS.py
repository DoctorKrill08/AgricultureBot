import serial
import time
from timer import Timer
from enum import Enum
import math
import re


def miles_to_inches(miles):
    return miles * 63360

class Direction(Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    def get_direction(char: str):
        if (char == Direction.NORTH):
            return Direction.NORTH
        if (char == Direction.EAST):
            return Direction.EAST
        if (char == Direction.SOUTH):
            return Direction.SOUTH
        if (char == Direction.WEST):
            return Direction.WEST

class CoordinateSystem(Enum):
    DECIMAL_DEGREES_MINUTES = "DDMM.MMMMM" #What gps read
    DECIMAL_DEGREES = "DD" #Google maps
    LOCAL = "LOCAL"
    LONGITUDE = "LONGITUDE"
    LATITUDE = "LATITUDE"
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

    def displacement(coordinates1,coordinates2):
        start_lat = coordinates2[0]
        start_lon = coordinates2[1]

        lat = coordinates1[0]
        lon = coordinates1[1]

        avg_lat = CoordinateSystem.average_coordinates(lat,start_lat)

        delta_lat = (lat - start_lat) * 69.1
        delta_lon = (lon - start_lon) * 69.1 * math.cos(avg_lat)

        delta_lat = miles_to_inches(delta_lat)
        delta_lon = miles_to_inches(delta_lon)

        distance = math.sqrt((delta_lat ** 2) + (delta_lon ** 2))

        return delta_lat,delta_lon,distance

    def average_coordinates(c1,c2):
        return (c2 + c1) / 2

    def cumulative_average_coordinates(coordinates):
        avg = 0
        for coordinate in coordinates:
            coordinate = coordinate
            avg += coordinate
        avg /= len(coordinates)
        return avg
    def recursive_average(prev_coordinate,coordinate,num_of_coords):
        if (num_of_coords <= 0):
            return coordinate
        return prev_coordinate + (coordinate - prev_coordinate)/num_of_coords




class GPSReceiver():
    ROVER = "ROVER"
    BASE = "BASE"

    NANO = "NANO"
    WINDOWS = "WINDOWS"

    BAUD_RATE = 115200

    POSITION_STREAM = '$GNGGA'
    RTK_STREAM = ''

    ROVER_PORTS = {
            NANO: '/dev/ttyACM1',
            WINDOWS : 'COM8',
    }
    BASE_PORTS = {
            NANO: '/dev/ttyACM2',
            WINDOWS : 'COM10',
    }

    def __init__(self,type):
        self.serial_ports = GPSReceiver.ROVER_PORTS
        if (type == GPSReceiver.BASE):
            self.serial_ports = GPSReceiver.BASE_PORTS
            #TBA add RTK stream logic
        self.type = type
        self.connected = False
        
        self.serial = self.serial_ports[self.NANO]

        self.longitude = 0
        self.latitude = 0
        self.quality = 0

        self.yaw = 0

        self.target_stream = GPSReceiver.POSITION_STREAM

    def start(self):
        print(self.serial_ports)
        self.connected = False
        for key,value in self.serial_ports.items():
            if (self.connected):
                return
            try:
                self.serial = serial.Serial(value,  self.BAUD_RATE, timeout=1)
                self.connected = True
                print(f"Connected to {self.type} RTK receiver via {key}: {value}")
            except:
                pass

    def read(self):
        if (not  self.connected):
            print(f"{self.type} NOT CONNECTED")
            return
        lines = self.serial.read_all().decode('utf-8', errors='ignore').strip()
        lines = re.split(r'(\n)',lines)
        print("--------")
        for line in (lines):
            if line.startswith(self.target_stream):
                lat,lon,quality = GPSReceiver.parse_gps(line)
                if (lat == None or lon == None or lat == "" or lon == ""):
                    return
                lat = CoordinateSystem.DDM_TO_DD(lat,CoordinateSystem.LATITUDE)
                lon = CoordinateSystem.DDM_TO_DD(lon,CoordinateSystem.LONGITUDE)
                self.start_position_found = True
                self.latitude = lat
                self.longitude = lon
                self.quality = quality
                print(self.status())
    
    def close(self):
        if (self.connected):
            self.serial.close()
        self.connected = False

    def status(self):
        return f"{self.type},connected:{self.connected},latitude:{self.latitude},longitude:{self.longitude},quality:{self.quality}-{GPSReceiver.int_to_quality(self.quality)}"

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
class GPS:

    rover = GPSReceiver(GPSReceiver.ROVER)
    base = GPSReceiver(GPSReceiver.BASE)


    PERIOD = 0.2 #Time inbetween readings
    timer = Timer()

    local_grid = [0,0]

    def global_to_local():
        return
    def local_to_global():
        return

    def start():
        GPS.rover.start()
        GPS.base.start()
    def close():
        GPS.rover.close()
        GPS.base.close()
    def status():
        GPS.rover.status()
        GPS.base.status()
    def signal_base_to_rover():
        waiting = GPS.base.serial.in_waiting
        if waiting:
            data = GPS.base.serial.read(waiting)

            print(f"Forwarding {len(data)} bytes")

            GPS.rover.serial.write(data)
            GPS.rover.serial.flush()
            print(f"Wrote {len(data)} bytes to rover")
    def update():
        GPS.rover.read()
       # GPS.base.read()

        if (GPS.rover.connected and GPS.base.connected):
            GPS.signal_base_to_rover()
        if (GPS.timer.time_passed() < GPS.PERIOD):
            time.sleep(GPS.PERIOD - GPS.timer.time_passed())
        GPS.timer.reset()
        


#To run:
#Windows: python -m System.GPS
#Linux: python3 -m System.GPS (I think)
if __name__ == "__main__":
    GPS.start()
    while True:
        GPS.update()