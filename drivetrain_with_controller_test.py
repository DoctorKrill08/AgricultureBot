import time
from System.robot import *


LOOP_TIME = 0.05 #How much time in between each loop, seconds

Robot.initiate()
time.sleep(1)
Robot.set_state(RobotState.GAMEPAD)
start = time.perf_counter()

while Robot.on:
    elapsed = time.perf_counter() - start
    sleep_time = LOOP_TIME - elapsed
    start = time.perf_counter()
    if sleep_time > 0:
        time.sleep(sleep_time)
    gamepad = Robot.gamepad
    Robot.update()
    if (gamepad == None):
        break