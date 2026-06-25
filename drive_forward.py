from System.robot import *
if __name__ == "__main__":
    Robot.turn_on()
    RUN_TIME = 3
    timer = Timer()
    time.sleep(.1)
    Robot.set_state(RobotState.AUTONOMOUS)
    time.sleep(.1)
    while (timer.time_passed() < RUN_TIME):
        Robot.joy_x = 0
        Robot.joy_y = 0.4
        Robot.update()
    Robot.turn_off()
