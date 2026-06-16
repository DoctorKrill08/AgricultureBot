from fastapi import FastAPI, WebSocket
from System.robot import *
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
            "type": "telemetry",
            **Robot.telemetry.model_dump()
        })

        await asyncio.sleep(0.1)

async def command_task(websocket: WebSocket):
    while True:

        data = await websocket.receive_json()
        print(data)
        if data["request"] == "SET_STATE":
            Robot.set_state(data["values"])
        elif data["request"] == "OFF":
            Robot.turn_off()
        elif data["request"] == "ON":
            Robot.turn_on()
        elif data["request"] == "gamepad":
            Robot.joy_x = data["values"]
            Robot.joy_y = data["values"]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print("CLIENT CONNECTING")

    await websocket.accept()

    print("CLIENT CONNECTED")

    await asyncio.gather(
        telemetry_task(websocket),
        command_task(websocket)
    )