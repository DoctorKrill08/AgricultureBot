import pyrplidarsdk
import time

# Create driver instance for serial connection
driver = pyrplidarsdk.RplidarDriver(port="COM3")

# Connect to the device
if not driver.connect():
    print("Failed to connect!")
    exit(1)

# Get device information
info = driver.get_device_info()
if info:
    print(f"Connected to RPLIDAR model {info.model}")
    print(f"Firmware: {info.firmware_version}")
    print(f"Hardware: {info.hardware_version}")
    print(f"Serial: {info.serial_number}")

# Check device health
health = driver.get_health()
if health:
    print(f"Device health: {health.status}")

# Start scanning
if driver.start_scan():
    print("Scanning started...")
    
    try:
        for i in range(100):  # Get 10 scans
            scan_data = driver.get_scan_data()
            if scan_data:
                angles, ranges, qualities = scan_data
                print(f"Scan {i+1}: {len(angles)} points")
            time.sleep(0.1)
    finally:
        #driver.stop_scan()
        #driver.disconnect()
        pass