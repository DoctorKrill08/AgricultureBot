from Drivetrain import Drivetrain
#from controller import XboxController
import time
#gamepad = XboxController()
Drivetrain.initiate()
Drivetrain.stop()
time.sleep(1)
end = False
Drivetrain.run(0,0.5)
time.sleep(10)
Drivetrain.run(0,-0.5)
time.sleep(10)
Drivetrain.stop()