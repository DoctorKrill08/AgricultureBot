from Drivetrain import Drivetrain
#from controller import XboxController
import time
#gamepad = XboxController()
Drivetrain.initiate()
Drivetrain.stop()
time.sleep(1)
Drivetrain.run(drive = 0, turn = 0.5)
time.sleep(10)
Drivetrain.run(drive = 0,turn = -0.5)
time.sleep(10)
Drivetrain.stop()