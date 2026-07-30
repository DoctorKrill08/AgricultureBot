from fastapi import FastAPI, WebSocket
from System.robot import Robot, RobotState,Localizer,Camera,Drivetrain
from System.Pathing import DynamicWindow
from System.interface_map import *
import asyncio
import time

app = FastAPI()


async def robot_loop():

    while True:
        Robot.update()
        await asyncio.sleep(0.05)

@app.on_event("startup")
async def startup():
    Robot.initiate()
    time.sleep(1)

    asyncio.create_task(robot_loop())


async def telemetry_task(websocket: WebSocket):
    while True:
        try:
            telemetry_dict = Robot.telemetry.model_dump(mode='json')
            
            payload = {
                "COMMAND": Command.TELEMETRY.value,
                **telemetry_dict
            }
            
            await websocket.send_json(payload)
                
        except Exception as e:
            print(f"Telemetry stream error: {e}")
            
        await asyncio.sleep(0.1)


async def command_task(websocket: WebSocket):
    while True:
        data = await websocket.receive_json()
        print(data)
        if data[COMMAND] == Command.SET_STATE.value:
            Robot.set_state(RobotState(data[VALUES]))
        elif data[COMMAND] == Command.OFF.value:
            Robot.turn_off()
        elif data[COMMAND] == Command.ON.value:
            Robot.initiate()
        elif data[COMMAND] == Command.JOYSTICK.value:
            Robot.set_joystick(data[VALUES])
        elif data[COMMAND] == Command.ADD_PATH.value or data[COMMAND] == Command.DELETE_PATH.value or data[COMMAND] == Command.DELETE_ALL_PATHS.value or data[COMMAND] == Command.SET_PATH_YAW.value or data[COMMAND] == Command.SET_PATH_INDEX.value:
            Robot.modify_path(data[COMMAND],data[VALUES])
        elif data[COMMAND] == Command.SET_CLEARANCE.value:
            DynamicWindow.CLEARANCE_SCORE = float(data[VALUES])
        elif data[COMMAND] == Command.SET_ANGLE_PENALTY.value:
            DynamicWindow.ANGLE_PENALTY = float(data[VALUES])
        elif data[COMMAND] == Command.SET_ANGLE_INCREMENT.value:
            DynamicWindow.ANGLE_INCREMENT = int(data[VALUES])
        elif data[COMMAND] == Command.SET_CHANGE_PENALTY.value:
            DynamicWindow.CHANGE_PENALTY = float(data[VALUES])
        elif data[COMMAND] == Command.SET_MAX_CLEARANCE.value:
            DynamicWindow.MAX_CLEARANCE = float(data[VALUES])
        elif data[COMMAND] == Command.SET_MAX_POWER.value:
            power = float(data[VALUES])
            if (power > 0.5):
                power = 0.5
            if (power < -0.5):
                power = -0.5
            Drivetrain.MAX_POWER = power
        await asyncio.sleep(0.05)
        
        

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print("CLIENT CONNECTING")

    await websocket.accept()

    print("CLIENT CONNECTED")

    await asyncio.gather(
        telemetry_task(websocket),
        command_task(websocket),
        await websocket.send_bytes(Camera.binary_frame)
    )
