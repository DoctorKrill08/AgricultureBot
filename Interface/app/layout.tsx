'use client'
import React, { useEffect, useRef, useState } from "react";
import './globals.css'
import Joystick from './joystick'
import Compass from './Compass'
import Mapping from './Mapping'
import GPS from './GPS'
import './interface_map'
import { COMMAND, VALUES, Command, RobotState, Telemetry } from "./interface_map";



export default function RobotControlPanel() {
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [telemetry, setTelemetry] = useState<Telemetry>({
    mode: "RESTING",
    x: 0,
    y: 0,
    vector_x: 0,
    vector_y: 0,
    heading: 0,
    arduino_connected: false,
    gps_data: "",
    obstacles: "N/A",
    paths: "N/A",
    status: "Disconnected",
  });

  const [connected, setConnected] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);

  const inputChange = (cmd: string) => (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      console.log(cmd)
      var input = parseFloat((event.target as HTMLInputElement).value);
      if (Number.isNaN(input)) {
        return
      }
      var input_str = String(input)
      sendCommand(cmd, input_str)
    }
  };

  useEffect(() => {
    // 1. Detect if the current page is served over HTTPS
    const isSecure = window.location.protocol === 'https:';
    const host = window.location.host;
    const wsProtocol = isSecure ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws`;
    const socket = new WebSocket(wsUrl);

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
    socket.binaryType = 'blob';
    socket.onmessage = (event) => {
      if (event.data instanceof Blob) {
        if (imgRef.current) {
          const blobUrl = URL.createObjectURL(event.data);

          // Cache the old URL to clean up memory
          const oldUrl = imgRef.current.src;
          imgRef.current.src = blobUrl;

          // Prevent severe memory leaks by revoking the old URL
          if (oldUrl.startsWith('blob:')) {
            URL.revokeObjectURL(oldUrl);
          }
        }
        return
      }
      try {
        const data = JSON.parse(event.data);
        if (data[COMMAND] === Command.TELEMETRY) {
          setTelemetry((prevTelemetry) => ({
            ...prevTelemetry,
            mode: data.mode ?? prevTelemetry.mode,
            x: data.x ?? prevTelemetry.x,
            y: data.y ?? prevTelemetry.y,
            vector_x: data.vector_x ?? prevTelemetry.vector_x,
            vector_y: data.vector_y ?? prevTelemetry.vector_y,
            heading: data.heading ?? prevTelemetry.heading,
            arduino_connected: data.arduino_connected ?? prevTelemetry.arduino_connected,
            gps_data: data.gps_data ?? prevTelemetry.gps_data,
            obstacles: data.obstacles ?? prevTelemetry.obstacles,
            paths: data.paths ?? prevTelemetry.paths,
            status: data.status ?? prevTelemetry.status,
          }));
        }
      } catch (error) {
        console.error("Failed to parse telemetry JSON:", error);
      }
    }
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
        [COMMAND]: command,
        [VALUES]: values,
      })
    );
  };

  const handleJoystickUpdate = (x: number, y: number) => {
    console.log("Joystick:", x, y);
    sendCommand(Command.JOYSTICK, `${x},${y}`)
  };



  return (
    <html>
      <body className="background">
        <div style={{
          display: "flex",
          width: '100vw',
          flexDirection: 'row',
          flexWrap: 'wrap'
        }}>
          <img ref={imgRef} style={{ width: '640px', height: '480px', transform: "scale(-1)" }} />
          <Joystick onMove={handleJoystickUpdate} />
          <div style={{ width: '400px', }}>
            <h2>Command</h2>

            <div>
              <button className="off-button" onClick={() => sendCommand(Command.OFF, "")}>
                Off
              </button>
              <button className="on-button" onClick={() => sendCommand(Command.ON, "")}>
                On
              </button>
              <button className="button" onClick={() => sendCommand(Command.SET_STATE, RobotState.RESTING)}>
                Resting
              </button>

              <button className="button" onClick={() => sendCommand(Command.SET_STATE, RobotState.GAMEPAD)}>
                Gamepad
              </button>

              <button className="button" onClick={() => sendCommand(Command.SET_STATE, RobotState.AUTONOMOUS)}>
                Autonomous
              </button>
              <button className="button" onClick={() => sendCommand(Command.SET_STATE, RobotState.MAP_CONTROL)}>
                Map Control
              </button>
              <br />
              ------ROBOT-------
              <br />
              Max Power:
              <input enterKeyHint="done" type="number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_MAX_POWER)} />
              <br />
              <br />
              -----Dynamic Window Approach------
              <br />
              Clearance Score:
              <input enterKeyHint="done" type="number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_CLEARANCE)} />
              <br />
              -----------
              <br />
              Angle Penalty:
              <input enterKeyHint="done" type="number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_ANGLE_PENALTY)} />
              <br />
              ---------
              <br />
              Change Penalty:
              <input enterKeyHint="done" type="number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_CHANGE_PENALTY)} />
              <br />
              -----------
              <br />
              MAX Clearance:
              <input enterKeyHint="done" type="number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_MAX_CLEARANCE)} />
              <br />
              -----------
              <br />
              Angle Increment:
              <input enterKeyHint="done" type="number" className="button" defaultValue={0} placeholder="..." onKeyDown={inputChange(Command.SET_ANGLE_INCREMENT)} />
              <br />


            </div>
          </div>
          <Compass yaw={telemetry.heading} />
          <Mapping bx={telemetry.x} by={telemetry.y} bYaw={telemetry.heading}
            vx={telemetry.vector_x} vy={telemetry.vector_y}
            mapData={telemetry.obstacles} sendCommand={sendCommand}
            pathData={telemetry.paths} />
          <GPS gpsData={telemetry.gps_data} />

          {/* Telemetry Section */}
          <div style={{ width: '400px', height: '800px' }}>
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
              <strong>Mode:</strong> {telemetry.mode}
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
              <strong>Net Vector X:</strong> {telemetry.vector_x}
            </div>

            <div>
              <strong>Net Vector Y:</strong> {telemetry.vector_y}
            </div>

            <div>
              <strong>OBSTACLES:</strong> {telemetry.obstacles}
            </div>

            <div>
              <strong>PATHS:</strong> {telemetry.paths}
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
