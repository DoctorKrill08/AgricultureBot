from enum import Enum
import os

class Device(Enum):
    DriveLeft = '1'
    DriveRight = '2'
    Battery = '3'
    Turret = '4'
    ShoulderLeft = '5'
    ShoulderRight = '6'
    Elbow = '7'
    Wrist = '8'
    ClawRot = '9'
    Claw = '10'
    Blade = '11'
class HardwareType(Enum):
    SERVO = 'S'
    MOTOR = 'M'
    BATTERY = 'B'
class Request(Enum):
    OFF = "0"
    SET = "1"
    GET = "2"


hardware_type_map = {}
hardware_type_map[Device.DriveLeft.value] = HardwareType.MOTOR.value
hardware_type_map[Device.DriveRight.value] = HardwareType.MOTOR.value
hardware_type_map[Device.Battery.value] = HardwareType.BATTERY.value
hardware_type_map[Device.Turret.value] = HardwareType.MOTOR.value
hardware_type_map[Device.ShoulderLeft.value] = HardwareType.MOTOR.value
hardware_type_map[Device.ShoulderRight.value] = HardwareType.MOTOR.value
hardware_type_map[Device.Elbow.value] = HardwareType.MOTOR.value
hardware_type_map[Device.Wrist.value] = HardwareType.SERVO.value
hardware_type_map[Device.ClawRot.value] = HardwareType.SERVO.value
hardware_type_map[Device.Claw.value] = HardwareType.SERVO.value
hardware_type_map[Device.Blade.value] = HardwareType.SERVO.value




#If you enjoy readable code, that dies below this point. TURN AWAY!



#GENERATE THE C++ HEADER FILE
def generate_arduino_header():
    header_content = """// AUTOMATICALLY GENERATED FILE - DO NOT EDIT DIRECTLY

// Input char value of device, ex. DriveLeft = '1', output type, ex. 'M' -> Motor
#ifndef COMMANDS_H
#define COMMANDS_H

char getType(char key){
    switch(key){
"""
    command_list = []
    for key,type in hardware_type_map.items():
        command_list.append(f"\n        case '{key}':\n         return '{type}';")
            
    header_content += "\n".join(command_list)
    header_content += "\n   };\n}\n#endif;"

    header_content += f"\nconst char SERVO_VALUE = '{HardwareType.SERVO.value}';"
    header_content += f"\nconst char MOTOR_VALUE = '{HardwareType.MOTOR.value}';"
    header_content += f"\nconst char BATTERY_VALUE = '{HardwareType.BATTERY.value}';"

    #make a struct request -> equivalent of that enum
    header_content += "\nstruct Request {"
    command_list.clear()
    for key,item in Request.__members__.items():
        command_list.append(f"\n    int {key} = {item.value};")
    header_content += "".join(command_list)
    header_content += "\n};"

    #make a struct Device -> equivalent of that enum
    header_content += "\nstruct Device {"
    command_list.clear()
    for key,item in Device.__members__.items():
        command_list.append(f"\n    int {key} = {item.value};")
    header_content += "".join(command_list)
    header_content += "\n};"

    # Save to libraries folder so that arduino can implement
    target_dir = "./libraries/translate"
    file_name = "translate.h"
    full_path = os.path.join(target_dir, file_name)

    with open(full_path, "w") as f:
        f.write(header_content)
    print("✓ Successfully generated translate.h for Arduino!")

if __name__ == "__main__":
    generate_arduino_header()

