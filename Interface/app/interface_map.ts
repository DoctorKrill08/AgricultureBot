export const Command = Object.freeze({
  OFF : "-1",
  TELEMETRY : "0",
  ON : "1",
  SET_STATE : "2",
  JOYSTICK : "3",
  SET_TARGET_POSE : "10",
  SET_TARGET_YAW : "11",
  SET_CLEARANCE : "12",
  SET_ANGLE_PENALTY : "13",

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
  vector_x : number;
  vector_y : number;
  heading : number;
  target_yaw : number;
  arduino_connected : boolean;
  gps_connected : boolean;
  map : string;
  status : string;

};
export const COMMAND = "0";
export const VALUES = "1";
export const INCHES_PER_NODE = "2";
