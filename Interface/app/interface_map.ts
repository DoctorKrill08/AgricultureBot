export const Command = Object.freeze({
  OFF : "-1",
  TELEMETRY : "0",
  ON : "1",
  SET_STATE : "2",
  JOYSTICK : "3",
  CAM_DRIVE_P : "4",
  CAM_TURN_P : "5",
  AUTO_TIME : "6",

});
export const RobotState = Object.freeze({
  RESTING : "RESTING",
  GAMEPAD : "GAMEPAD",
  AUTONOMOUS : "AUTONOMOUS",

});
export type Telemetry ={
  mode : string;
  battery : number;
  longitude : number;
  latitude : number;
  heading : number;
  arduino_connected : boolean;
  gps_connected : boolean;
  status : string;

};
export const COMMAND = "0";
export const VALUES = "1";
