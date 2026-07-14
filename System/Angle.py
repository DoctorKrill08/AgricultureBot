import math
def add_angle(a1,a2):
    if (a1 > math.pi):
        a1 -= 2 * math.pi
    if (a2 > math.pi):
        a2 -= 2 * math.pi
    if (a1 < -math.pi):
        a1 += 2 * math.pi
    if (a2 < -math.pi):
        a2 += 2 * math.pi
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