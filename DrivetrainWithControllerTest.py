from controller import XboxController
import time
from Drivetrain import Drivetrain

xbox_controller = XboxController()

TARGET_HZ = 20
DT = 1 / TARGET_HZ

on = True

Drivetrain.initiate()
Drivetrain.stop()
time.sleep(1)

while on and xbox_controller.is_connected():
    start = time.perf_counter()
    if (xbox_controller.a_was_pressed()):
        on = False
    if (xbox_controller.is_connected()):
        Drivetrain.run(drive = xbox_controller.LeftJoystickY, turn = xbox_controller.RightJoystickX)
    elapsed = time.perf_counter() - start
    sleep_time = DT - elapsed

    if sleep_time > 0:
        time.sleep(sleep_time)
Drivetrain.stop()