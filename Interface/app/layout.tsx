'use client'
import React, { useEffect, useRef, useState } from "react";
import './globals.css'
import Joystick from './joystick'
import Compass from './Compass'
import Map from './Map'
import './interface_map'
import { COMMAND,VALUES, Command, RobotState ,Telemetry} from "./interface_map";



export default function RobotControlPanel() {
  const [telemetry, setTelemetry] = useState<Telemetry>({
    mode: "RESTING",
    battery: 0,
    x: 0,
    y: 0,
    tx: 0,
    ty: 0,
    target_yaw: 0,
    heading: 0,
    arduino_connected: false,
    gps_connected: false,
    map: "N/A",
    status: "Disconnected",
  });

  const [connected, setConnected] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);

  const inputChange = (cmd: string) => (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault(); 
      console.log(cmd)
      var input = parseFloat((event.target as HTMLInputElement).value);
      if (Number.isNaN(input)){
        return
      }
      var input_str = String(input)
      sendCommand(cmd,input_str)
    }
  };

  //Nano -> 172.17.0.1
  //Rokoko ->10.54.132.8, 10.54.132.13,10.54.132.53
  useEffect(() => {
    const socket = new WebSocket("ws://10.54.132.34:8000/ws");

    socketRef.current = socket;

    socket.onopen = () => {
      console.log("Connected to robot");
      setConnected(true);
    };

    socket.onclose = () => {
      console.log("Disconnected from robot");
      setConnected(false);
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data[COMMAND] === Command.TELEMETRY) {
        setTelemetry({
          mode: data.mode,
          battery: data.battery,
          x: data.x,
          y: data.y,
          tx: data.tx,
          ty: data.ty,
          target_yaw: data.target_yaw,
          heading: data.heading,
          arduino_connected: data.arduino_connected,
          gps_connected: data.gps_connected,
          map: data.map,
          status: data.status,
        });
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const sendCommand = (command: string, values: string) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn("Socket not connected");
      return;
    }

    socketRef.current.send(
      JSON.stringify({
        [COMMAND] : command,
        [VALUES] : values,
      })
    );
  };

   const handleJoystickUpdate = (x: number, y: number) => {
    console.log("Joystick:", x, y);
    sendCommand(Command.JOYSTICK,`${x},${y}`)
  };

  const handleMapCommand = (x: number, y: number) => {
    console.log("MAP:", x, y);
    sendCommand(Command.SET_TARGET_POSE,`${x},${y}`)
  };


  return (
    <html>
      <body className="background">
        <div>
          {/* Command Section */}
          <div>
            <h2>Command</h2>

            <div>
              <button className="off-button" onClick={() => sendCommand(Command.OFF,"")}>
                Off
              </button>
              <button className="on-button" onClick={() => sendCommand(Command.ON,"")}>
                On
              </button>
              <button className="button" onClick={() => sendCommand(Command.SET_STATE,RobotState.RESTING)}>
                Resting
              </button>

              <button className="button" onClick={() => sendCommand(Command.SET_STATE,RobotState.GAMEPAD)}>
                Gamepad
              </button>

              <button className="button" onClick={() => sendCommand(Command.SET_STATE,RobotState.AUTONOMOUS)}>
                Autonomous
              </button>
              <button className="button" onClick={() => sendCommand(Command.SET_STATE,RobotState.MAP_CONTROL)}>
                Map Control
              </button>
              <br/> 
              ------ROBOT-------
              <br/>
              TARGET_YAW:
              <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_TARGET_YAW)}/>  
              <br/>
               --------------
              <br/>
              TURN_P:
              <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_TURN_P)}/>  
              <br/>
               --------------
              <br/>
              DIVE_P:
              <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_DRIVE_P)}/>  
              <br/>
               --------------
              <br/>
              MIN_DISTANCE:
              <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_MIN_DISTANCE)}/>  
              <br/> 
              --------------
              <br/>
              AUTO_TIME:           
              <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.AUTO_TIME)}
              />      
              <br/>
              -----CAMERA------
              <br/>
              CAMERA DRIVE P:
              <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.CAM_DRIVE_P)}/>
              <br/>
              --------------
              <br/>
              CAMERA TURN P:
              <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.CAM_TURN_P)}/>  
              <br/>
              
                       
            </div>

            <Joystick onMove={handleJoystickUpdate}/>
            <Compass  yaw= {telemetry.heading}/>
            <Map bx = {telemetry.x} by = {telemetry.y} tx = {telemetry.tx} ty = {telemetry.ty}  bYaw = {telemetry.heading} tYaw = {telemetry.target_yaw} map_data = {telemetry.map} onMove = {handleMapCommand}/>

          </div>
          {/* Telemetry Section */}
          <div>
            <h2>Telemetry</h2>

            <div>
              <strong>Client Connected:</strong>{" "}
              {connected ? "True" : "False"}
            </div>

             <div>
              <strong>Arduino Connected:</strong> {" "}
              {telemetry.arduino_connected ? "True" : "False"}
            </div>

             <div>
              <strong>GPS Connected:</strong> {" "}
              {telemetry.gps_connected ? "True" : "False"}
            </div>

            <div>
              <strong>Mode:</strong> {telemetry.mode}
            </div>

            <div>
              <strong>Battery:</strong> {telemetry.battery}
            </div>

            <div>
              <strong>X:</strong> {telemetry.x}
            </div>

            <div>
              <strong>Y:</strong> {telemetry.y}
            </div>

            <div>
              <strong>Heading:</strong> {telemetry.heading}
            </div>

            <div>
              <strong>TX:</strong> {telemetry.tx}
            </div>

            <div>
              <strong>TY:</strong> {telemetry.ty}
            </div>
            <div>
              <strong>Target Yaw:</strong> {telemetry.target_yaw}
            </div>
            <div>
              <strong>MAP DATA:</strong> {telemetry.map}
            </div>
            <div>
              <strong>Status: </strong> {telemetry.status}
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
