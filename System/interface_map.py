# generate_js_enums.py
from enum import Enum
from pydantic import BaseModel

class Command(Enum):
    OFF = "-1"
    TELEMETRY = "0"
    ON = "1"
    SET_STATE = "2"
    JOYSTICK = "3"

    CAM_DRIVE_P = "4"
    CAM_TURN_P = "5"
    CAM_MIN_VISIBLE_PIXELS = "6"
    CAM_TOO_CLOSE = "7"
    CAM_MIN_HORIZONTAL = "8"

    AUTO_TIME = "9"

    IMU_TRANS_ACCEL_THRESH_X = "10"
    IMU_TRANS_ACCEL_THRESH_Y = "11"
    IMU_TRANS_ACCEL_THRESH_Z = "12"

    IMU_ROT_ACCEL_THRESH_X = "13"
    IMU_ROT_ACCEL_THRESH_Y = "14"
    IMU_ROT_ACCEL_THRESH_Z = "15"

    IMU_ROT_MOVE_THRESH_X = "16"
    IMU_ROT_MOVE_THRESH_Y = "17"
    IMU_ROT_MOVE_THRESH_Z = "18"

    IMU_TRANS_MOVE_THRESH_X = "19"
    IMU_TRANS_MOVE_THRESH_Y = "20"
    IMU_TRANS_MOVE_THRESH_Z = "21"
        

class RobotState(Enum):
    RESTING = "RESTING"
    GAMEPAD = "GAMEPAD"
    AUTONOMOUS = "AUTONOMOUS"

class Telemetry(BaseModel):
    mode: str
    battery: float
    longitude: float
    latitude: float
    heading: float
    arduino_connected: bool
    gps_connected: bool
    status: str

class ClientInputs(BaseModel):
    command: str
    joy_x: float
    joy_y: float


COMMAND = '0'
VALUES = '1'


def python_type_to_typescript(type:str):
    print(type)
    if (type == 'str'):
        return 'string'
    if (type == 'float' or type == 'int'):
        return 'number'
    if (type == 'bool'):
        return "boolean"
    if (type == 'None' or type == None):
        return "Null"
    return "Null"
def clean_annotations(annotation:str):
    annotation = annotation.removeprefix("<class '")
    annotation = annotation.removesuffix("'>")
    return annotation

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

    output += f"export type {Telemetry.__name__} ="
    output += "{\n"
    for name,data_type in Telemetry.model_fields.items():
        data_type.annotation = str(data_type.annotation)
        data_type.annotation = clean_annotations(data_type.annotation)
        data_type.annotation = python_type_to_typescript(data_type.annotation)
        output += f'  {name} : {data_type.annotation};\n'
    output += "\n};\n"

    output += f'export const COMMAND = "{COMMAND}";\n'
    output += f'export const VALUES = "{VALUES}";\n'

    print("MADE JS FILE")
    
    with open("../Interface/app/interface_map.ts", "w") as file:
        file.write(output)