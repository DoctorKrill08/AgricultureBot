from Hardware import *
motor = Motor("1")
motor.forward()
motor.set(0.5) #50 percent
time.sleep(2)
motor.stop()
time.sleep(2)
#servo.set(100)
motor.set(-1) #Reverse at 100 percent
time.sleep(2)
#servo.set(0)
motor.stop()
close_arduino()