from fastapi import FastAPI
from System.robot import *

app = FastAPI()

@app.get("/user_inputs")
def get_inputs(inputs: ClientInputDataTypes):
    command_to_robot(inputs.command)
    return {"Command Successfull"}

@app.put("/telemtry")
def set_telemtry():
    return {}

#while Robot.on():
   # Robot.update()
