from rplidar import *   
from System.Constants import * 
import threading

class Lidar:
    MAX_DISTANCE = 18
    ANGLE_RANGE = 160 #Degrees
    POS_ON_BOT = 10
    port = "COM3"
    BAUD_RATE = 1000000
    ANGLE_INCREMENT = 2 #Degrees
    lidar = None

    latest_scan = []
    obstacles = []

    lock = None
    thread = None
    running = False
    def start():
        Lidar.lock = threading.Lock()
        Lidar.thread = None
        Lidar.running = True

        Lidar.thread = threading.Thread(
            target=Lidar.lidar_thread,
            daemon=True
        )
        Lidar.thread.start()
        print("Lidar threading started")
        

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
    
    def lidar_thread():
        #Repeat as loing as lidar is supposed to be running
        while Lidar.running:
            time.sleep(2)
            Lidar.lidar = None
            #connecting the lidar
            try:
                Lidar.lidar = RPLidar(Lidar.port,Lidar.BAUD_RATE)
                print("Conencted to Lidar")
                Lidar.running = True
            except Exception as e:
                print("Failed to connect to Lidar: ", e) 
            time.sleep(1)
            #read the lidar, shoulld loop until program ends, but data could be corrupted
            try:
                for scan in Lidar.lidar.iter_scans():
                    if not Lidar.running:
                        break
                    with Lidar.lock:
                        Lidar.latest_scan = scan
            except Exception as e:
                print("FAILED TO SCAN LIDAR: ",e)
            finally:
                if (isinstance(Lidar.lidar,RPLidar)): 
                    try:
                        Lidar.lidar.stop()
                        Lidar.lidar.disconnect()
                    except Exception as e:
                        print("Lidar closing error: ",e)
            time.sleep(2)
    def stop():
        Lidar.running = False
        # Wait for reader thread to completely exit
        if (
            Lidar.thread is not None
            and Lidar.thread.is_alive()
        ):

            Lidar.thread.join(
                timeout=5
            )
        Lidar.thread = None
        
    def calculate(bot_x,bot_y,yaw):
        prev_angle = 0
        with Lidar.lock:
            print("latest scan ", Lidar.latest_scan)
            if len(Lidar.latest_scan) == 0:
                return
            if Lidar.latest_scan == None:
                return
            for scan in Lidar.latest_scan:
                if (len(scan) < 3):
                    continue
                quality = scan[0]
                angle = scan[1]
                distance = scan[2]
                #angle is in degrees initially
                if (not angle < Lidar.ANGLE_RANGE / 2 and not angle > 360 - Lidar.ANGLE_RANGE / 2):
                    continue
                angle = math.radians(angle)
                distance = mm_to_inches(distance)
                if quality < 5:
                    continue
                if (distance > Lidar.MAX_DISTANCE):
                    continue
                if (distance <= 1):
                    continue
                if (math.degrees(shortest_angular_distance(angle,prev_angle)) < Lidar.ANGLE_INCREMENT):
                    continue
                prev_angle = angle #rads
                # Ignore low-quality points
                x,y = Lidar.relative_to_global(bot_x,bot_y,yaw,distance,angle)
                Lidar.obstacles.append([x,y])

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
            print(Lidar.latest_scan)
            if (elapsed < RATE):
                time.sleep(RATE - elapsed)
    finally:
        Lidar.stop()
