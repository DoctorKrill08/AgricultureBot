import serial
import time
from timer import Timer
from enum import Enum
import math
import re
from pyubx2 import UBXReader, UBX_PROTOCOL

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

class GPS:


    INITIAL_POSITION_FOUND_READING_THRESHOLD = 50
    connected = False
    base_station_connected = False
    NANO = "NANO"
    WINDOWS = "WINDOWS"
    SERIAL_PORTS = {
        NANO: '/dev/ttyACM1',
        WINDOWS : 'COM8'
    }
    port = SERIAL_PORTS[NANO]
    BAUD_RATE = 115200 # Default ZED-F9P rate is 115200
    chip = None
    PERIOD = 0.1 #Time inbetween readings
    timer = Timer()

    longitude = 0
    latitude = 0

    NS = Direction.NORTH #North or South
    EW = Direction.WEST  #East or west

    yaw = 0

    POSITION_STREAM = '$GNGGA'
    RTK_STREAM = ''


    start_position = [0,0]
    start_position_found = False
    reading_count = 0


    local_grid = [0,0]

    def global_to_local():
        return
    def local_to_global():
        return
    def parse_gps(line :str):
        latitude = GPS.latitude
        longitude = GPS.longitude
        type,_,line = line.partition(f',')
        if (type == GPS.POSITION_STREAM):
            time,_,line = line.partition(",")
            latitude,_,line = line.partition(",")
            north_south,_,line = line.partition(",")
            longitude,_,line = line.partition(",")
            east_west,_,line = line.partition(",")
            quality,_,line = line.partition(",")

            """
            print("TYPE",type)
            print("TIME: ", time)
            print("LATITIUDE: ",latitude)
            print("N/S: ",north_south)
            print("LONGITUDE: ",longitude)
            print("E/W: ",east_west)
            print("FIX QUALITY: ",quality)
            """

            return latitude,longitude


    def status():
        return f"START_POSITION_READY: {GPS.start_position_found} READING_COUNT: {GPS.reading_count}\n \
            LAT: {GPS.latitude} LON: {GPS.longitude}\n \
            START_LAT: {GPS.start_position[0]} START_LONG: {GPS.start_position[1]}\n \
            DELTA_LAT: {GPS.local_grid[0]} DELTA_LON: {GPS.local_grid[1]}"

    def connect_gps():
        GPS.connected = False
        GPS.start_position_found = False
        GPS.start_position = []
        for key,value in GPS.SERIAL_PORTS.items():
            if (GPS.connected):
                return
            try:
                GPS.chip = serial.Serial(value, GPS.BAUD_RATE, timeout=1)
                print(f"Connected to ArduSimple RTK receiver via {key}: {value}")
                GPS.port = key
                GPS.connected = True
                GPS.timer.reset()
                GPS.position_stream_timer.reset()
            except:
                pass
    def read():
        if (not GPS.connected):
            print("GPS NOT CONNECTED")
            return
        lines = GPS.chip.read_all().decode('utf-8', errors='ignore').strip()
        lines = re.split(r'(\n)',lines)
        print("--------")
        for line in (lines):
            if line.startswith(GPS.POSITION_STREAM):
                lat,lon = GPS.parse_gps(line)
                lat = CoordinateSystem.DDM_TO_DD(lat,CoordinateSystem.LATITUDE)
                lon = CoordinateSystem.DDM_TO_DD(lon,CoordinateSystem.LONGITUDE)
                if (GPS.reading_count < GPS.INITIAL_POSITION_FOUND_READING_THRESHOLD):
                    GPS.latitude = CoordinateSystem.recursive_average(GPS.latitude,lat,GPS.reading_count)
                    GPS.longitude = CoordinateSystem.recursive_average(GPS.longitude,lon,GPS.reading_count)
                    GPS.start_position = [GPS.latitude,GPS.longitude]
                    GPS.reading_count += 1
                else:
                    GPS.start_position_found = True
                    GPS.latitude = lat
                    GPS.longitude = lon
                d_lat,d_lon,distance = CoordinateSystem.displacement([GPS.latitude,GPS.longitude],GPS.start_position)
                GPS.local_grid = [d_lat,d_lon]
                print("DISTANCE: ", distance)
                print(GPS.status())


    def update():
        GPS.read()
        if (GPS.timer.time_passed() < GPS.PERIOD):
            time.sleep(GPS.PERIOD - GPS.timer.time_passed())
        GPS.timer.reset()
        
    def close():
        if (GPS.connected):
            GPS.chip.close()
        GPS.connected = False


#To run:
#Windows: python -m System.GPS
#Linux: python3 -m System.GPS (I think)
if __name__ == "__main__":
    GPS.connect_gps()
    while True:
        GPS.update()
    GPS.close()