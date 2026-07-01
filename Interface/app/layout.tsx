'use client'
import React, { useEffect, useRef, useState } from "react";
import './globals.css'
import Joystick from './joystick'
import './interface_map'
import { COMMAND, Command, RobotState, VALUES ,Telemetry} from "./interface_map";



export default function RobotControlPanel() {
  const [telemetry, setTelemetry] = useState<Telemetry>({
    mode: "RESTING",
    battery: 0,
    longitude: 0,
    latitude: 0,
    heading: 0,
    arduino_connected: false,
    gps_connected: false,
    status: "Disconnected",
  });

  const [connected, setConnected] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);

  const [driveP, setDriveP] = useState<number>(0);

  const [turnP, setTurnP] = useState<number>(0);
  const [autoTime, setAutoTime] = useState<number>(0);

  const inputChange = (cmd: string) => (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault(); 
      console.log(cmd)
      var input = parseFloat((event.target as HTMLInputElement).value);
      if (Number.isNaN(input)){
        return
      }
      var input_str = String(input)
      if (cmd == Command.CAM_DRIVE_P){
        setDriveP(input)
      }else if(cmd == Command.CAM_TURN_P){
        setTurnP(input)
      }else if (cmd == Command.AUTO_TIME){
        setAutoTime(input)
      }
      sendCommand(cmd,input_str)
    }
  };

  //Nano -> 172.17.0.1
  //Rokoko ->10.54.132.8, 10.54.132.13
  useEffect(() => {
    const socket = new WebSocket("ws://172.17.0.1:8000/ws");

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
          longitude: data.longitude,
          latitude: data.latitude,
          heading: data.heading,
          arduino_connected: data.arduino_connected,
          gps_connected: data.gps_connected,
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
        "0": command,
        "1": values,
      })
    );
  };

   const handleJoystickUpdate = (x: number, y: number) => {
    console.log("Joystick:", x, y);
    sendCommand(Command.JOYSTICK,`${x},${y}`)
  };


  return (
    <html>
      <body className="background">
        <div>

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
              <strong>Longitude:</strong> {telemetry.longitude}
            </div>

            <div>
              <strong>Latitude:</strong> {telemetry.latitude}
            </div>

            <div>
              <strong>Heading:</strong> {telemetry.heading}
            </div>

            <div>
              <strong>Status:</strong> {telemetry.status}
            </div>
          </div>

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
              <input type = "number" className="button" defaultValue={driveP} placeholder="..." onKeyDown={inputChange(Command.CAM_DRIVE_P)}
              />
                DRIVE_P: {driveP}
              <input type = "number" className="button" defaultValue={turnP} placeholder="..." onKeyDown={inputChange(Command.CAM_TURN_P)}
              />                TURN_P: {turnP}
              <input type = "number" className="button" defaultValue={autoTime} placeholder="..." onKeyDown={inputChange(Command.AUTO_TIME)}
              />                AUTO_TIME: {autoTime}
            </div>

            <Joystick onMove={handleJoystickUpdate}/>

          </div>
        </div>
      </body>
    </html>
  );
}
