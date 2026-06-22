'use client'
import React, { useEffect, useRef, useState } from "react";
import './globals.css'
import Joystick from './joystick'


type TelemetryData = {
  mode: string;
  battery: number;
  longitude: number;
  latitude: number;
  heading: number;
  arduino_connected: boolean;
  gamepad_connected: boolean;
  status: string;
};

export default function RobotControlPanel() {
  const [telemetry, setTelemetry] = useState<TelemetryData>({
    mode: "RESTING",
    battery: 0,
    longitude: 0,
    latitude: 0,
    heading: 0,
    arduino_connected: false,
    gamepad_connected: false,
    status: "Disconnected",
  });

  const [connected, setConnected] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);

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
      if (data.type === "telemetry") {
        setTelemetry({
          mode: data.mode,
          battery: data.battery,
          longitude: data.longitude,
          latitude: data.latitude,
          heading: data.heading,
          arduino_connected: data.arduino_connected,
          gamepad_connected: data.gamepad_connected,
          status: data.status,
        });
      }
    };

    return () => {
      socket.close();
    };
  }, []);

  const sendCommand = (request: string, values: string) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn("Socket not connected");
      return;
    }

    socketRef.current.send(
      JSON.stringify({
        request: request,
        values: values,
      })
    );
  };

   const handleJoystickUpdate = (x: number, y: number) => {
    x = Math.pow(x,3)
    y = Math.pow(y,3)
    console.log("Joystick:", x, y);
    sendCommand("JOYSTICK",`${x},${y}`)
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
              <strong>Gamepad Connected:</strong> {" "}
              {telemetry.gamepad_connected ? "True" : "False"}
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
              <button className="off-button" onClick={() => sendCommand("OFF","")}>
                Off
              </button>
              <button className="on-button" onClick={() => sendCommand("ON","")}>
                On
              </button>
              <button className="button" onClick={() => sendCommand("SET_STATE","RESTING")}>
                Resting
              </button>

              <button className="button" onClick={() => sendCommand("SET_STATE","GAMEPAD")}>
                Gamepad
              </button>

              <button className="button" onClick={() => sendCommand("SET_STATE","AUTONOMOUS")}>
                Autonomous
              </button>
            </div>

            <Joystick onMove={handleJoystickUpdate}/>

          </div>
        </div>
      </body>
    </html>
  );
}