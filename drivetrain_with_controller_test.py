import time
from System.robot import *

Robot.initiate()
time.sleep(0.5)
Robot.set_state(RobotState.GAMEPAD)

while Robot.on:
    gamepad = Robot.gamepad
    Robot.update()
    print("Update")
    if (gamepad == None):
        break