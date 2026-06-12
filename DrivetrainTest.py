from Subsystems import Drivetrain
import time
Drivetrain.initiate()
Drivetrain.stop()
time.sleep(1)
Drivetrain.run(drive = 0, turn = 0.5)
time.sleep(3)
Drivetrain.run(drive = 0,turn = -0.5)
time.sleep(3)
Drivetrain.stop()
