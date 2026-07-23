from rplidar import *   
from System.Constants import * 
import pyrplidarsdk

class Lidar:
    MAX_DISTANCE = 40
    ANGLE_RANGE = 160 #Degrees
    POS_ON_BOT = 10
    port = "COM3"
    BAUD_RATE = 1000000
    ANGLE_INCREMENT = 2 #Degrees
    driver = None

    obstacles = []

    connected = False
    def start():
        Lidar.driver = pyrplidarsdk.RplidarDriver(port="COM3")
        Lidar.connected = False
        # Connect to the device
        if not Lidar.driver.connect():
            print("Failed to connect!")
            return

        # Get device information
        info = Lidar.driver.get_device_info()
        if info:
            print(f"Connected to RPLIDAR model {info.model}")
            print(f"Firmware: {info.firmware_version}")
            print(f"Hardware: {info.hardware_version}")
            print(f"Serial: {info.serial_number}")

        # Check device health
        health = Lidar.driver.get_health()
        if health:
            print(f"Device health: {health.status}")
        Lidar.driver.start_scan()
        

    def relative_to_global(x,y,yaw,distance,angle):
        #yaw and angle in rads
        angle = yaw + angle
        while angle > math.pi:
            angle -= (2 * math.pi)
        while angle < -math.pi:
            angle += (2 * math.pi)
        x += distance * math.cos(angle)
        y += distance * math.sin(angle)
        return x,y

    def stop():
        if (not Lidar.connected):
            return
        Lidar.driver.stop_scan()
        Lidar.driver.disconnect()
    
    def status():
        return f"---LIDAR---\nCONNECTED: {Lidar.connected}\nobstacles len{len(Lidar.obstacles)}"
        
    def calculate(bot_x,bot_y,yaw):
        prev_angle = 0
        if (not isinstance(Lidar.driver,pyrplidarsdk.RplidarDriver)):
            return      
        scan_data = Lidar.driver.get_scan_data()
        if (not scan_data):
            return
        Lidar.obstacles.clear()
        angles, ranges, qualities = scan_data
        for i in range(len(angles)):
            angle = angles[i] #rads
            distance = ranges[i] #meters
            quality = qualities[i] #idk bro
            #angle is in rads
            if (not angle < math.radians(Lidar.ANGLE_RANGE / 2) and not angle > math.radians(360 - Lidar.ANGLE_RANGE / 2)):
                continue
            distance = meters_to_inches(distance)
            if quality < 5:
                #print("low quality: ",quality)
                continue
            if (distance > Lidar.MAX_DISTANCE):
                #print("too far",distance)
                continue
            if (distance <= 1):
                #print("too close",distance)
                continue
            if (abs(math.degrees(shortest_angular_distance(angle,prev_angle))) < Lidar.ANGLE_INCREMENT):
                #print("angle difference to small ",math.degrees(shortest_angular_distance(angle,prev_angle)) )
                continue
            prev_angle = angle #rads
            # Ignore low-quality points
            x,y = Lidar.relative_to_global(bot_x,bot_y,yaw,distance,angle)
            Lidar.obstacles.append([x,y])
        #print(Lidar.obstacles)

#Windows: python -m System.Lidar
RATE = 1
if __name__ == "__main__":
    Lidar.start()
    start_time = time.perf_counter()
    try:
        while True:
            elapsed = time.perf_counter() - start_time 
            Lidar.calculate(0,0,0)
            print("----")
            start_time = time.perf_counter()
            if (elapsed < RATE):
                time.sleep(RATE - elapsed)
    finally:
        Lidar.stop()
