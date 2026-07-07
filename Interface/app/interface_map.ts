export const Command = Object.freeze({
  OFF : "-1",
  TELEMETRY : "0",
  ON : "1",
  SET_STATE : "2",
  JOYSTICK : "3",
  CAM_DRIVE_P : "4",
  CAM_TURN_P : "5",
  AUTO_TIME : "9",
  SET_TARGET_POSE : "10",

});
export const RobotState = Object.freeze({
  RESTING : "RESTING",
  GAMEPAD : "GAMEPAD",
  AUTONOMOUS : "AUTONOMOUS",
  MAP_CONTROL : "MAP_CONTROL",

});
export type Telemetry ={
  mode : string;
  battery : number;
  x : number;
  y : number;
  tx : number;
  ty : number;
  heading : number;
  arduino_connected : boolean;
  gps_connected : boolean;
  status : string;

};
export const COMMAND = "0";
export const VALUES = "1";
