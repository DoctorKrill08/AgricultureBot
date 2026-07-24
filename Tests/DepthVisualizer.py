import cv2
import numpy as np
import pyrealsense2 as rs
import time

WIDTH = 640
HEIGHT = 480
FPS = 15
MIN_DISTANCE = 0.1
MAX_DISTANCE = 3

prev_img = np.array([0,0,0])

def start():
    pipe = rs.pipeline()
    cfg  = rs.config()

    cfg.enable_stream(rs.stream.color, WIDTH,HEIGHT, rs.format.bgr8, FPS)
    cfg.enable_stream(rs.stream.depth, WIDTH,HEIGHT, rs.format.z16, FPS)

    pipe.start(cfg)
    return pipe
count = 0
def read(pipe):
    frame = pipe.wait_for_frames()
    depth_frame = frame.get_depth_frame()
    color_frame = frame.get_color_frame()

    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    depth_cm = cv2.applyColorMap(cv2.convertScaleAbs(depth_image,
                                    alpha = 0.03), cv2.COLORMAP_JET)
    cv2.imshow('rgb', color_image)
    cv2.imshow('depth', depth_cm)


def overlay_filter(prev_image,depth_image,start):
   # depth_intrin = depth_image.profile.as_video_stream_profile().get_intrinsics()
   # prev_intrin = prev_image.profile.as_video_stream_profile().get_intrinsics()
    if (not start):
        return depth_image
    filtered = depth_image
    for x in range(WIDTH):
        for y in range(HEIGHT):
            prev_z = prev_image.get_distance(x,y)
            z = depth_image.get_distance(x,y)
            diff = z - prev_z
            if (abs(diff) > 3):
                filtered[y,x] = [0,0,0]
            if (z <= MAX_DISTANCE):
                filtered[y,x] = [0,0,0]
                continue
            if (z >= MIN_DISTANCE):
                filtered[y,x] = [0,0,0]
                continue
    return filtered
def contour_filter():
    pass


if __name__ == "__main__":
    pipe = start()
    while True:
        read(pipe)
        if cv2.waitKey(1) == ord('q'):
            break
    pipe.stop()


