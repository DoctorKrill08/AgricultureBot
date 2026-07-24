from fastapi import FastAPI, WebSocket
from System.robot import Robot, RobotState,Localizer,Camera,Drivetrain
from System.Pathing import DynamicWindow
from System.interface_map import *
import asyncio


app = FastAPI()


async def robot_loop():

    while True:
        Robot.update()
        await asyncio.sleep(0)

@app.on_event("startup")
async def startup():
    Robot.initiate()
    asyncio.create_task(robot_loop())


async def telemetry_task(websocket: WebSocket):
    while True:
        await websocket.send_json({
            COMMAND: Command.TELEMETRY.value,
            **Robot.telemetry.model_dump()
        })

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
        elif data[COMMAND] == Command.SET_TARGET_YAW.value:
            Localizer.target_yaw = float(data[VALUES])
        elif data[COMMAND] == Command.SET_CLEARANCE.value:
            DynamicWindow.CLEARANCE_SCORE = float(data[VALUES])
        elif data[COMMAND] == Command.SET_ANGLE_PENALTY.value:
            DynamicWindow.ANGLE_PENALTY = float(data[VALUES])
        

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print("CLIENT CONNECTING")

    await websocket.accept()

    print("CLIENT CONNECTED")

    await asyncio.gather(
        telemetry_task(websocket),
        command_task(websocket)
    )