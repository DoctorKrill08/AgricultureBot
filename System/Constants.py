import math
ROBOT_WIDTH = 20 #inches
ROBOT_HEIGHT = 8
CAMERA_Y = 5
CAMERA_DISTANCE_FROM_ROBOT = 7
GROUND_HEIGHT = 2
CAMERA_HORIZONTAL_FOV = 87 #Degrees
CAMERA_VERTICAL_FOV = 53 #Degrees
CAMERA_MAX_DEPTH = 118 # Inches
CAMERA_MIN_DEPTH = 8 #Inches
def round_nearest(number, base):
    return round(number / base) * base
def meters_to_inches(meters):
    return meters * 39.3700787402
def mm_to_inches(mm):
    return mm / 25.4
def angle_wrap(angle):
    if (angle > math.pi):
        return angle - (2 * math.pi)
    if (angle < -math.pi):
        return angle + (2 * math.pi)
    return angle
def add_angle(a1,a2):
    if (a1 > math.pi):
        a1 -= 2 * math.pi
    if (a2 > math.pi):
        a2 -= 2 * math.pi
    if (a1 < -math.pi):
        a1 += 2 * math.pi
    if (a2 < -math.pi):
        a2 += 2 * math.pi
    if (a2 == 0):
        return a1
    sum = 0
    if (a1 / a2) < 0:
        pos = a1
        neg = a2
        if (a1 < 0):
            pos = a2
            neg = a1
        
        neg += (2 * math.pi)
        sum = pos + neg
    else:
        sum = a1 + a2
    if (sum > 2 * math.pi):
        sum -= 2 * math.pi
    if (sum < -2 * math.pi):
        sum += 2 * math.pi
    return sum
def shortest_angular_distance(angle1, angle2):
    diff = (angle2 - angle1 + math.pi) % (2*math.pi) - math.pi
    return (diff)