import math
import time
import pygame
from System.timer import Timer
def to_scale(drive,turn):
    if (drive < 0):
        drive = 0
    if (abs(drive) + abs(turn) < MAX_POWER):
        return drive,turn
    sum = abs(drive) + abs(turn)
    scale = MAX_POWER/sum
    return (drive * scale),(turn * scale)

def estimate_pose(current_pose,drive,turn,deltaT):
    theta = current_pose.yaw
    theta += ((turn * deltaT) * TURN_SPEED)
    if (theta > math.pi):
        theta -= (2 * math.pi)
    if (theta < -math.pi):
        theta += (2 * math.pi)
    print("r:" ,theta)
    current_pose.yaw = theta
    current_pose.x += drive * deltaT * DRIVE_SPEED * math.cos(theta)
    current_pose.y += drive * deltaT * DRIVE_SPEED * math.sin(theta)
    return current_pose

def make_triangle(current_pose):
    pixels = current_pose.pixels()
    center_x = pixels.x + current_pose.size/2
    center_y = pixels.y + current_pose.size/2
    r = int(current_pose.size * 2)
    #Equilateral Triangle
    ANGLE =  math.radians(120)
    theta = current_pose.yaw
    ax = int(center_x + (r * math.cos(theta)))
    ay = int(center_y + (r * math.sin(theta)))

    bx = int(center_x + ((r) * math.cos(theta + ANGLE)))
    by = int(center_y + ((r) * math.sin(theta + ANGLE)))

    cx = int(center_x + ((r) * math.cos(theta - ANGLE)))
    cy = int(center_y + ((r) * math.sin(theta - ANGLE)))

    return pygame.Vector2(ax,ay),pygame.Vector2(bx,by),pygame.Vector2(cx,cy)


def sub_angle(a1,a2):
    difference = a1 - a2
    if (difference == 0):
        return difference
    if ((a1 > 0 and a2 > 0) or (a1 < 0 and a2 < 0)):
        return difference
    negative = a1
    if (a1 > 0):
        negative = a2
    if (abs(negative) < math.pi / 2):
        return difference
    if (a1 < 0):
        a1 += (2 * math.pi)
    if (a2 < 0):
        a2 += (2 * math.pi)
    return (a1 - a2)



    



pygame.init()

SCREEN_WIDTH = int(400)
SCREEN_HEIGHT = int(400)

PIXEL_PER_INCH = 10

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

def pixels_to_inches(x,y):
    x = int(x / PIXEL_PER_INCH)
    y = int(y / PIXEL_PER_INCH)
    return x,y
def inches_to_pixels(x,y):
    x = x * PIXEL_PER_INCH
    y = y * PIXEL_PER_INCH
    return x,y

class Pose:
    x = 0
    y = 0
    yaw = 0
    size = 10
    def __init__(self,x,y,yaw):
        self.x = x
        self.y = y
        self.yaw = yaw
    def set(self,x,y,yaw):
        self.x = x
        self.y = y
        self.yaw = yaw
    def status(self):
        return f"x: {self.x} y: {self.y} yaw: {self.yaw}"
    def pixels(self):
        x,y = inches_to_pixels(self.x,self.y)
        return Pose(x,y,self.yaw)
    @staticmethod
    def distance(pose1,pose2):
        x1 = pose1.x
        x2 = pose2.x
        y1 = pose1.y
        y2 = pose2.y
        return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))

START_POSE = Pose(0,0,0)
current_pose = START_POSE
target_pose = Pose(10,10,0)
DISTANCE_THRESHOLD = 1

DRIVE_SPEED = 10
TURN_SPEED = 4

DRIVE_P = 0.08
TURN_P = 1
TURN_D = 0.1

MAX_POWER = 1


robot_rect = pygame.Rect(target_pose.pixels().x,target_pose.pixels().y,target_pose.size,target_pose.size)
target_rect = pygame.Rect(target_pose.pixels().x,target_pose.pixels().y,current_pose.size,current_pose.size)

DELTA_T = 0.1
distance = Pose.distance(current_pose,target_pose)
print(current_pose.status())
print(distance)
run = True
timer = Timer()
while run:
    screen.fill(BLACK)
    target_rect.x,target_rect.y = inches_to_pixels(target_pose.x,target_pose.y)
    robot_rect.x,robot_rect.y = inches_to_pixels(current_pose.x,current_pose.y)
    pygame.draw.polygon(screen,RED,make_triangle(current_pose))
    pygame.draw.rect(screen,BLUE,robot_rect)
    pygame.draw.rect(screen,GREEN,target_rect)


    for event in (pygame.event.get()):
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos
            print(click_pos)
            x,y = pixels_to_inches(click_pos[0],click_pos[1])
            target_pose.set(x,y,0)
        

    distance = Pose.distance(current_pose,target_pose)
    deltaX = target_pose.x - current_pose.x
    deltaY = target_pose.y - current_pose.y
    lookAt = math.atan2(deltaY,deltaX)
    deltaYaw = sub_angle(lookAt,current_pose.yaw)
    if (distance < DISTANCE_THRESHOLD):
        deltaYaw *= (distance / DISTANCE_THRESHOLD)
        distance *= (distance / DISTANCE_THRESHOLD)



    turn = deltaYaw * TURN_P
    drive = distance * DRIVE_P * math.cos(deltaYaw)
    drive,turn = to_scale(drive,turn)

    current_pose = estimate_pose(current_pose,drive,turn,DELTA_T)
    prev_delta_yaw = deltaYaw

    print("turn: ", turn)
    print("drive: ",drive)
    print("lookAt: ", lookAt)
    print("deltaX",deltaX)
    print("deltaY",deltaY)
    print("distance",distance)
    print("deltaYaw",deltaYaw)
    print(current_pose.status())
    pygame.display.update()
    elapsed = timer.time_passed()
    timer.reset()
    if (elapsed < DELTA_T):
        time.sleep(DELTA_T - elapsed)

pygame.quit()