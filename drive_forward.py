from System.robot import *
from System.Camera import Camera
if __name__ == "__main__":
    Robot.turn_on()
    Camera.start()
    RUN_TIME = 10
    time.sleep(2)
    timer = Timer()
    Robot.set_state(RobotState.AUTONOMOUS)
    time.sleep(.1)
    while (timer.time_passed() < RUN_TIME):
        Robot.joy_x = 0
        Robot.joy_y = 0.35
        if (Camera.to_close):
            Robot.joy_x = 0
            Robot.joy_y = 0
        Robot.update()
        Camera.read()
    Robot.turn_off()
