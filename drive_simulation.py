import math
import time
import pygame
from System.timer import Timer

class Pose:
    x = 0
    y = 0
    yaw = 0
    size = 10
    def __init__(self,x,y,yaw = 0,size = size):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.size = size
    def set(self,x,y,yaw):
        self.x = x
        self.y = y
        self.yaw = yaw
    def status(self):
        return f"x: {self.x} y: {self.y} yaw: {self.yaw}"
    def pixels(self):
        x,y = inches_to_pixels(self.x,self.y)
        return Pose(x,y,self.yaw)
    def add(self,p2):
        self.x += p2.x
        self.y += p2.y
    @staticmethod
    def calculate_angle(p1,p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        return math.atan2(dy,dx)
    @staticmethod
    def distance(pose1,pose2):
        x1 = pose1.x
        x2 = pose2.x
        y1 = pose1.y
        y2 = pose2.y
        return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))
    

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
    current_pose.yaw = theta
    current_pose.x += drive * deltaT * DRIVE_SPEED * math.cos(theta)
    current_pose.y += drive * deltaT * DRIVE_SPEED * math.sin(theta)
    return current_pose

def make_triangle(current_pose):
    pixels = current_pose.pixels()
    center_x = pixels.x
    center_y = pixels.y
    r = int(current_pose.size/2)
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
        if (difference > math.pi):
            difference -= (2 * math.pi)
        if (difference < -math.pi):
            difference += (2 * math.pi)
        return difference
    negative = a1
    flip = 1
    if (a1 > 0):
        negative = a2
    if (abs(negative) < math.pi / 2):
        if (difference > math.pi):
            difference -= (2 * math.pi)
        if (difference < -math.pi):
            difference += (2 * math.pi)
        return difference
    if (a1 < 0):
        a1 += (2 * math.pi)
    if (a2 < 0):
        a2 += (2 * math.pi)
    difference = a1 - a2
    if (difference > math.pi):
        difference -= (2 * math.pi)
    if (difference < -math.pi):
        difference += (2 * math.pi)
    return difference * flip

def draw_points(points,color,show_index = False):
    for i in range(len(points)):
        point = points[i]
        target_rect = pygame.Rect(point.pixels().x - point.size/2,point.pixels().y - point.size/2,point.size,point.size)
        pygame.draw.rect(screen,color,target_rect)
        if (show_index):
            text_surface = game_font.render(str(i), True, WHITE)
            screen.blit(text_surface,(target_rect.x  ,target_rect.y - 30))


class Camera:
    VISION_RANGE_FORWARD = 30 #inches
    VISION_RANGE_WIDTH = 25 #Inches
    CAMERA_FORWARD_POS = 10 #Inches

    OBSTACLE_MAX_DISTANCE = 60 #Inches

    STOP_DISTANCE = 10

    obstacle_vector = Pose(0,0)

    obstacle_in_view = False
    camera_obstacles = []

    center = Pose(0,0)

    a = Pose(0,0)
    b = Pose(0,0)
    c = Pose(0,0)
    d = Pose(0,0)

    random_direction = None

    def line(p1,p2,x):
        m = (p2.y - p1.y)/(p2.x - p1.x)
        result = (m * (x - p1.x) + p1.y)
        return result

    def make_view_points():
        ANGLE = math.pi / 2
        theta = current_pose.yaw
        f = Camera.VISION_RANGE_FORWARD
        r = Camera.VISION_RANGE_WIDTH / 2
        center = Pose(current_pose.x + Camera.CAMERA_FORWARD_POS * math.cos(theta),current_pose.y + Camera.CAMERA_FORWARD_POS * math.sin(theta))
        Camera.center = center
        a = Pose(0,0)
        b = Pose(0,0)
        c = Pose(0,0)
        d = Pose(0,0)
        a.x = center.x + r * math.cos(theta + ANGLE)
        a.y = center.y + r * math.sin(theta + ANGLE)

        b.x = center.x + r * math.cos(theta - ANGLE)
        b.y = center.y + r * math.sin(theta - ANGLE)

        c.x = b.x + f * math.cos(theta)
        c.y = b.y + f * math.sin(theta)

        d.x = a.x + f * math.cos(theta)
        d.y = a.y + f * math.sin(theta)
        return a,b,c,d

    def get_poses():
        #print("a: ",pa.status())
        #print("b: ",pb.status())
        #print("c: ",pc.status())
        #print("d: ",pd.status())
        #print("--------")
        return [Camera.a,Camera.b,Camera.c,Camera.d]
    def point_is_within_view(point,a,b,c,d):
        x = point.x
        y = point.y
        if (a.y > b.y and a.x < b.x):
            return (y < Camera.line(a,d,x) and y > Camera.line(b,c,x) and y < Camera.line(d,c,x) and y > Camera.line(a,b,x))
        if (a.y > b.y and a.x > b.x):
            return (y < Camera.line(a,d,x) and y > Camera.line(b,c,x) and y > Camera.line(d,c,x) and y < Camera.line(a,b,x))
        if (a.y < b.y and a.x > b.x):
            return (y > Camera.line(a,d,x) and y < Camera.line(b,c,x) and y > Camera.line(d,c,x) and y < Camera.line(a,b,x))
        if (a.y < b.y and a.x < b.x):
            return (y > Camera.line(a,d,x) and y < Camera.line(b,c,x) and y < Camera.line(d,c,x) and y > Camera.line(a,b,x))
        return False
    def update():
        Camera.a,Camera.b,Camera.c,Camera.d = Camera.make_view_points()
        Camera.obstacle_in_view = False
        Camera.obstacle_vector.x = 0
        Camera.obstacle_vector.y = 0 
        p = 100
        #Camera.camera_obstacles = []
        for obstacle in obstacles:
            #print("Obstacle: ",obstacle.status())
            if (Camera.point_is_within_view(obstacle,Camera.a,Camera.b,Camera.c,Camera.d)):
                Camera.obstacle_in_view = True
                Camera.camera_obstacles.append(obstacle)
        for obstacle in (Camera.camera_obstacles):
            d = Pose.distance(obstacle,current_pose)
            if (d > Camera.OBSTACLE_MAX_DISTANCE):
                Camera.camera_obstacles.remove(obstacle)
                continue
            
            theta = Pose.calculate_angle(obstacle,current_pose)
            Camera.obstacle_vector.x += ((Camera.STOP_DISTANCE ** 2)/(d ** 2)) * math.cos(theta)
            Camera.obstacle_vector.y += ((Camera.STOP_DISTANCE ** 2)/(d ** 2)) * math.sin(theta)

        if (len(Camera.camera_obstacles) > 0):
            Camera.obstacle_vector.x /= (len(Camera.camera_obstacles)/p)
            Camera.obstacle_vector.y /= (len(Camera.camera_obstacles)/p)


    



pygame.init()
game_font = pygame.font.SysFont("Arial", 20)
SCREEN_WIDTH = int(600)
SCREEN_HEIGHT = int(600)

PIXEL_PER_INCH = 1

RED = (255,0,0)
PURPLE = (255,0,255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

def pixels_to_inches(x=0,y=0):
    x = int(x / PIXEL_PER_INCH)
    y = int(y / PIXEL_PER_INCH)
    return x,y
def inches_to_pixels(x=0,y=0):
    x = x * PIXEL_PER_INCH
    y = y * PIXEL_PER_INCH
    return x,y


ROBOT_SIZE = 20
ROBOT_SIZE_PIXELS = ROBOT_SIZE * PIXEL_PER_INCH

START_POSE = Pose(100,100,0,size = ROBOT_SIZE_PIXELS)
current_pose = START_POSE
target_pose = Pose(200,200,0)

MIN_DISTANCE_THRESHOLD = 1
MAX_DISTANCE_THRESHOLD = 30

DRIVE_SPEED = 24 #Inches per second
TURN_SPEED = 1 #

DRIVE_P = 0.07
TURN_P = 10
TURN_D = 0.1

MAX_POWER = 1

targets = []
targets.append(target_pose)
target_index = 0

obstacles = []


robot_rect = pygame.Rect(target_pose.pixels().x,target_pose.pixels().y,ROBOT_SIZE_PIXELS/2,ROBOT_SIZE_PIXELS/2)

DELTA_T = 0.1
distance = Pose.distance(current_pose,target_pose)
print(current_pose.status())
print(distance)
run = True
timer = Timer()
can_see_obstacle = False
while run:
    Camera.update()
    screen.fill(BLACK)
    robot_rect.x,robot_rect.y = inches_to_pixels(current_pose.x,current_pose.y)
    robot_rect.x -= ROBOT_SIZE_PIXELS/4
    robot_rect.y -= ROBOT_SIZE_PIXELS/4
    pygame.draw.polygon(screen,BLUE,make_triangle(current_pose))
    pygame.draw.rect(screen,RED,robot_rect)
    draw_points(targets,GREEN,show_index=True)
    draw_points(obstacles,RED)
    draw_points(Camera.camera_obstacles,YELLOW)
    draw_points(Camera.get_poses(),PURPLE)

    target_pose = targets[target_index]

    for event in (pygame.event.get()):
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos
            print(click_pos)
            x,y = pixels_to_inches(click_pos[0],click_pos[1])
            if (event.button == pygame.BUTTON_RIGHT):
                targets.append(Pose(x,y,0))
            elif (event.button == pygame.BUTTON_LEFT):
                obstacles.append(Pose(x,y,0,size=5))
        

    distance = Pose.distance(current_pose,target_pose)
    lookAt = Pose.calculate_angle(current_pose,target_pose)


    lookVector = Pose(MAX_DISTANCE_THRESHOLD * math.cos(lookAt),MAX_DISTANCE_THRESHOLD * math.sin(lookAt))
    lookVector.add(Camera.obstacle_vector)
    #if (abs(lookVector) < 0)
    target_angle = math.atan2(lookVector.y,lookVector.x)
    deltaYaw = sub_angle(target_angle,current_pose.yaw)
    if (distance < MIN_DISTANCE_THRESHOLD):
        deltaYaw *= (distance / MIN_DISTANCE_THRESHOLD)
        distance *= (distance / MIN_DISTANCE_THRESHOLD)
        if (len(targets) > 1):
            targets.pop(target_index)
    


    turn = (deltaYaw * TURN_P)
    drive = (distance * DRIVE_P * math.cos(deltaYaw))
    drive,turn = to_scale(drive,turn)

    current_pose = estimate_pose(current_pose,drive,turn,DELTA_T)
    prev_delta_yaw = deltaYaw

    #print("Obstacles: ",can_see_obstacle)
    #print("lookAt: ", lookAt)
    #print("deltaYaw",deltaYaw)
    #print(current_pose.pixels().status())
    pygame.display.update()
    elapsed = timer.time_passed()
    timer.reset()
    if (elapsed < DELTA_T):
        time.sleep(DELTA_T - elapsed)

pygame.quit()