import serial
import time


# Open serial port (adjust port name and baudrate to match your setup)
base_radio = serial.Serial(port='/dev/ttyUSB0', baudrate=57600, timeout=1)

while True:
    base_radio.write(b'Hello Drone!\n')
    time.sleep(2.0)
