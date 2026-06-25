from robot import *
if __name__ == "__main__":
    Robot.turn_on()
    RUN_TIME = 3000
    timer = Timer()
    time.sleep(.1)
    Robot.set_state(RobotState.AUTONOMOUS)
    while (timer.time_passed() < RUN_TIME):
        Robot.joy_x = 0
        Robot.joy_y = 0.25
        Robot.update()
    Robot.turn_off()