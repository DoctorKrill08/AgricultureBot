# generate_js_enums.py
import json
from System.robot import RobotState

from enum import StrEnum, IntEnum

class Command(StrEnum):
    OFF = "-1"
    TELEMETRY = "0"
    ON = "1"
    SET_STATE = "2"
    JOYSTICK = "3"

COMMAND = "COMMAND"
VALUES = "VALUES"



#JavaScript Enum generator below

