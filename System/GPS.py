import serial
import time
from timer import Timer

class GPS:
    connected = False
    base_station_connected = False
    NANO = "NANO"
    WINDOWS = "WINDOWS"
    SERIAL_PORTS = {
        NANO: '/dev/ttyACM0',
        WINDOWS : 'COM4'
    }
    port = SERIAL_PORTS[NANO]
    BAUD_RATE = 115200 # Default ZED-F9P rate is 115200
    chip = None
    TARGET_LINE = '$GPGGA'
    PERIOD = 0.2 #Time inbetween readings
    timer = Timer()

    longitude = 0
    latitude = 0
    yaw = 0

    def global_to_local():
        return
    def local_to_global():
        return
    def parse_gps(line):
        return

    def connect_gps():
        for key,value in GPS.SERIAL_PORTS.items():
            try:
                GPS.chip = serial.Serial(value, GPS.BAUD_RATE, timeout=1)
                print(f"Connected to ArduSimple RTK receiver via {key}: {value}")
                GPS.port = key
                GPS.connected = True
                GPS.timer.reset()
            except:
                GPS.connected = False
    def read():
        if (not GPS.connected):
            print("GPS NOT CONNECTED")
            return
        line = GPS.chip.readline().decode('utf-8', errors='ignore').strip()
        print(line)
        if line.startswith(GPS.TARGET_LINE):
            print(f"{GPS.TARGET_LINE}: ", line)
    def update():
        GPS.read()
        if (GPS.timer.time_passed() < GPS.PERIOD):
            time.sleep(GPS.PERIOD - GPS.timer.time_passed())
        
    def close():
        if (GPS.connected):
            GPS.chip.close()
        GPS.connected = False
        