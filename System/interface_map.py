# generate_js_enums.py
from enum import Enum

class Command(Enum):
    OFF = "OFF"
    TELEMETRY = "TELEMETRY"
    ON = "ON"
    SET_STATE = "SET_STATE"
    JOYSTICK = "JOYSTICK"

class RobotState(Enum):
    RESTING = "RESTING"
    GAMEPAD = "GAMEPAD"
    AUTONOMOUS = "AUTONOMOUS"

COMMAND = "COMMAND"
VALUES = "VALUES"



#JavaScript Enum generator below
if __name__ == "__main__":
    output = f"export const {Command.__name__} = Object.freeze("
    output += "{\n"
    for member in Command:
        output += f'  {member.name} : "{member.value}",\n'
    output += "\n});\n"

    output += f"export const {RobotState.__name__} = Object.freeze("
    output += "{\n"
    for member in RobotState:
        output += f'  {member.name} : "{member.value}",\n'
    output += "\n});\n"

    output += f'export const COMMAND = "{COMMAND}";\n'
    output += f'export const VALUES = "{VALUES}";\n'

    print("MADE JS FILE")
    
    with open("Interface/app/interface_map.js", "w") as file:
        file.write(output)