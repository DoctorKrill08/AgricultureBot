from System.robot import *
class Auto():
    timer = None
    RUN_TIME = 10
    def __init__(self):
        self.timer = Timer()
        self.elapsed = 0
    def loop(self):
        Robot.update()
    def end(self):
        Robot.set_state(RobotState.RESTING)
class DriveForwardWithCamera(Auto):
    def loop(self):
        Robot.joy_x = 0
        Robot.joy_y = 0.35
        if (Camera.to_close or not Camera.on):
            Robot.joy_x = 0
            Robot.joy_y = 0
        Robot.update()
        if (self.timer.time_passed() > self.RUN_TIME):
            self.end()
    def end(self):
        Camera.stop()
        Robot.set_state(RobotState.RESTING)