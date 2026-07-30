# generate_js_enums.py
from enum import Enum
from pydantic import BaseModel

class Command(Enum):
    OFF = "OFF"
    TELEMETRY = "TELEMETRY"
    ON = "ON"
    SET_STATE = "SET_STATE"
    JOYSTICK = "JOYSTICK"

    SET_MAX_POWER = "SET_MAX_POWER"

    DELETE_ALL_PATHS = "DELETE_ALL_PATHS"
    DELETE_PATH = "DELETE_PATH"
    ADD_PATH = "ADD_PATH"
    SET_PATH_YAW = "SET_PATH_YAW"
    SET_PATH_INDEX = "SET_PATH_INDEX"
    
    SET_CLEARANCE = "SET_CLEARANCE"
    SET_ANGLE_PENALTY = "SET_ANGLE_PENALTY"
    SET_CHANGE_PENALTY = "SET_CHANGE_PENALTY"
    SET_ANGLE_INCREMENT = "SET_ANGLE_INCREMENT"
    SET_MAX_CLEARANCE = "SET_MAX_CLEARANCE"
        

class RobotState(Enum):
    RESTING = "RESTING"
    GAMEPAD = "GAMEPAD"
    AUTONOMOUS = "AUTONOMOUS"
    MAP_CONTROL = "MAP_CONTROL"

class Telemetry(BaseModel):
    mode: str
    x: float
    y: float
    vector_x : float
    vector_y : float
    heading: float
    arduino_connected: bool
    gps_data: str
    paths : str
    obstacles: str
    status: str
    camera_stream: str

class ClientInputs(BaseModel):
    command: str
    joy_x: float
    joy_y: float


COMMAND = '0'
VALUES = '1'

class MapKey(Enum):
    OBSTACLE = "O"
    SAVED_OBSTACLE = "S"
    EMPTY = "E"
    CURRENT_PATH = "G"
    PATH_IN_QUE = "Q"

class GPSKey(Enum):
    LATITUDE = "LATITUDE"
    LONGITUDE = "LONGITUDE"
INCHES_PER_NODE = 2


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

    output += f"export const {MapKey.__name__} = Object.freeze("
    output += "{\n"
    for member in MapKey:
        output += f'  {member.name} : "{member.value}",\n'
    output += "\n});\n"

    output += f"export const {GPSKey.__name__} = Object.freeze("
    output += "{\n"
    for member in GPSKey:
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
    output += f'export const INCHES_PER_NODE = "{INCHES_PER_NODE}";\n'

    print("MADE TS FILE")
    
    with open("Interface/app/interface_map.ts", "w") as file:
        file.write(output)