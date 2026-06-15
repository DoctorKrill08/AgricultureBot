import time
from System.robot import *


LOOP_TIME = 0.05 #How much time in between each loop, seconds

Robot.initiate()
time.sleep(1)
Robot.set_state(RobotState.GAMEPAD)

while Robot.on:
    start = time.perf_counter()
    elapsed = time.perf_counter() - start
    sleep_time = LOOP_TIME - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)
    gamepad = Robot.gamepad
    Robot.update()
    if (gamepad == None):
        break