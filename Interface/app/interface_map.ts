export const Command = Object.freeze({
  OFF : "OFF",
  TELEMETRY : "TELEMETRY",
  ON : "ON",
  SET_STATE : "SET_STATE",
  JOYSTICK : "JOYSTICK",
  DELETE_ALL_PATHS : "DELETE_ALL_PATHS",
  DELETE_PATH : "DELETE_PATH",
  ADD_PATH : "ADD_PATH",
  SET_PATH_YAW : "SET_PATH_YAW",
  SET_PATH_INDEX : "SET_PATH_INDEX",
  SET_CLEARANCE : "SET_CLEARANCE",
  SET_ANGLE_PENALTY : "SET_ANGLE_PENALTY",

});
export const RobotState = Object.freeze({
  RESTING : "RESTING",
  GAMEPAD : "GAMEPAD",
  AUTONOMOUS : "AUTONOMOUS",
  MAP_CONTROL : "MAP_CONTROL",

});
export const MapKey = Object.freeze({
  OBSTACLE : "O",
  SAVED_OBSTACLE : "S",
  EMPTY : "E",
  CURRENT_PATH : "G",
  PATH_IN_QUE : "Q",

});
export const GPSKey = Object.freeze({
  LATITUDE : "LATITUDE",
  LONGITUDE : "LONGITUDE",

});
export type Telemetry ={
  mode : string;
  x : number;
  y : number;
  vector_x : number;
  vector_y : number;
  heading : number;
  arduino_connected : boolean;
  gps_data : string;
  paths : string;
  obstacles : string;
  status : string;

};
export const COMMAND = "0";
export const VALUES = "1";
export const INCHES_PER_NODE = "2";
