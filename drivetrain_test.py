
from System.robot import *
Robot.turn_on()
time.sleep(.5)
Drivetrain.run(drive = 0.1,turn =0)
time.sleep(2)
Robot.turn_off()
