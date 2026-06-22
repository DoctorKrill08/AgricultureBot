from fastapi import FastAPI, WebSocket
from System.robot import Robot, RobotState
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
            COMMAND: Command.TELEMETRY,
            **Robot.telemetry.model_dump()
        })

        await asyncio.sleep(0.1)

async def command_task(websocket: WebSocket):
    while True:

        data = await websocket.receive_json()
        print(data)
        if data[COMMAND] == Command.SET_STATE:
            Robot.set_state(RobotState(data[VALUES]))
        elif data[COMMAND] == Command.OFF:
            Robot.turn_off()
        elif data[COMMAND] == Command.ON:
            Robot.turn_on()
        elif data[COMMAND] == Command.JOYSTICK:
            Robot.set_joystick(data[VALUES])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print("CLIENT CONNECTING")

    await websocket.accept()

    print("CLIENT CONNECTED")

    await asyncio.gather(
        telemetry_task(websocket),
        command_task(websocket)
    )