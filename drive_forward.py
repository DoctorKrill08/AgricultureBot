from System.robot import *
from System.Localizer import Camera
if __name__ == "__main__":
    Robot.initiate()
    RUN_TIME = 10
    timer = Timer()
    #Robot.set_state(RobotState.AUTONOMOUS)
    Robot.set_state(RobotState.GAMEPAD)
    time.sleep(.1)
    time.sleep(1)
    while (timer.time_passed() < RUN_TIME):
        Robot.joy_y = 0.35
        Robot.update()
    Robot.turn_off()
