import pyrealsense2 as rs
import numpy as np
import cv2
def meters_to_inches(meters):
    return meters * 39.3701
class Camera:
    MIN_DISTANCE = 20 #inches
    FPS = 30
    distance = 0
    WIDTH = 640
    HEIGHT = 480
    CENTER_X = int(WIDTH / 2)
    CENTER_Y = int(HEIGHT / 2)
    WIDTH_RANGE = 100
    MAX_HEIGHT = HEIGHT - 100
    MIN_HEIGHT = 100
    SPACE_BETWEEN_RAYS = int(8)
    MIN_NUM_OF_CLOSE_RAYS = 30
    to_close = False
    pipe = None
    on = False
    def start():
        try:
            Camera.pipe = rs.pipeline()
            cfg  = rs.config()

            cfg.enable_stream(rs.stream.color, Camera.WIDTH,Camera.HEIGHT, rs.format.bgr8, Camera.FPS)
            cfg.enable_stream(rs.stream.depth, Camera.WIDTH,Camera.HEIGHT, rs.format.z16, Camera.FPS)

            Camera.pipe.start(cfg)
            Camera.on = True
        except:
            Camera.on = False
    def read():
        Camera.to_close = False
        if (not Camera.on):
            return
        frame = Camera.pipe.wait_for_frames()
        depth_frame = frame.get_depth_frame()
        color_frame = frame.get_color_frame()

        canvas_black = np.zeros((Camera.HEIGHT, Camera.WIDTH, 3), dtype=np.uint8)
        canvas_black[20, 20] = [0, 0, 255]
        Camera.pixels_within_distance(canvas_black,depth_frame)

        #cv2.imshow('to close', canvas_black)

    def stop():
        Camera.pipe.stop()
        Camera.on = False
    def pixels_within_distance(canvas,depth_frame):
        close_rays = 0
        for x in range(Camera.CENTER_X - Camera.WIDTH_RANGE, Camera.CENTER_X + Camera.WIDTH_RANGE, Camera.SPACE_BETWEEN_RAYS):
            for y in range(Camera.MIN_HEIGHT,Camera.MAX_HEIGHT, Camera.SPACE_BETWEEN_RAYS): 
                distance = meters_to_inches(depth_frame.get_distance(x, y))
                if (distance == 0):
                    continue
                if distance < Camera.MIN_DISTANCE:
                    close_rays = close_rays + 1
                    canvas[y-(Camera.SPACE_BETWEEN_RAYS):y+(Camera.SPACE_BETWEEN_RAYS), x-(Camera.SPACE_BETWEEN_RAYS):x+(Camera.SPACE_BETWEEN_RAYS)] = [0, 0, 255]
        if (close_rays > Camera.MIN_NUM_OF_CLOSE_RAYS):
            Camera.to_close = True
            print("TO CLOSE")
        else:
            print("GOOD")
            canvas[0:20,0:20] = [0,255,0]


        
if __name__ == "__main__":
    Camera.start()
    while True:
        Camera.read()
        if cv2.waitKey(1) == ord('q'):
            break
    Camera.stop()
