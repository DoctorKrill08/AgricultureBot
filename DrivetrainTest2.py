from Drivetrain import Drivetrain
#from controller import XboxController
import time
#gamepad = XboxController()
Drivetrain.initiate()
Drivetrain.stop()
time.sleep(1)
end = False
i = 0

while i < 100:
    Drivetrain.run(0,0.5 - (i/100 * 0.5))
    i = i + 1
    print(i)
    time.sleep(0.05)
Drivetrain.stop()