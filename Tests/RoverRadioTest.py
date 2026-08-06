import serial

# Open serial port (adjust port name and baudrate to match your setup)
rover_radio = serial.Serial(port='/dev/radio', baudrate=57600, timeout=1)

while True:
  if rover_radio.in_waiting > 0:
    data = rover_radio.readline()
    print(data.decode('utf-8', errors='ignore').strip())
