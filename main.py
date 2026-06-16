from fastapi import FastAPI, WebSocket
from System.robot import *
import asyncio


app = FastAPI()


async def robot_loop():

    while Robot.on:
        Robot.update()
        await asyncio.sleep(0)

@app.on_event("startup")
async def startup():
    Robot.initiate()
    asyncio.create_task(robot_loop())


async def telemetry_task(websocket: WebSocket):
    while True:

        telemetry = TelemetryDataTypes(
            mode=Robot.state.value,
            battery=12.4,
            longitude=10,
            latitude=0,
            heading=0,
            status="Running",
            fps=20,
            ping=10
        )

        await websocket.send_json({
            "type": "telemetry",
            **telemetry.model_dump()
        })

        await asyncio.sleep(0.1)

async def command_task(websocket: WebSocket):
    while True:

        data = await websocket.receive_json()
        print(data)
        if data["type"] == "command":
            command_to_robot(data["command"])

        elif data["type"] == "joystick":
            Robot.joy_x = data["joy_x"]
            Robot.joy_y = data["joy_y"]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print("CLIENT CONNECTING")

    await websocket.accept()

    print("CLIENT CONNECTED")

    await asyncio.gather(
        telemetry_task(websocket),
        command_task(websocket)
    )