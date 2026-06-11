import serial
import time

# 1. Establish the serial connection
# Ensure the baudrate (9600) matches the Arduino sketch exactly
arduino = serial.Serial(port='COM5', baudrate=9600, timeout=1)

# Allow time for the physical connection to initialize
time.sleep(2)

def send_command(command):
    # Serial communication only accepts bytes, so we must encode the string
    arduino.write(command.encode('utf-8'))
    
    # Read the response back from the Arduino
    response = arduino.readline().decode('utf-8').strip()
    print(f"Arduino says: {response}")

try:
    print("Sending '1' to turn on LED...")
    send_command('1')
    time.sleep(2)
    
    print("Sending '0' to turn off LED...")
    send_command('0')

finally:
    # Always close the port when done so other programs can access it
    arduino.close()