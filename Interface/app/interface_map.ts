export const Command = Object.freeze({
  OFF : "-1",
  TELEMETRY : "0",
  ON : "1",
  SET_STATE : "2",
  JOYSTICK : "3",
  CAM_DRIVE_P : "4",
  CAM_TURN_P : "5",
  CAM_MIN_VISIBLE_PIXELS : "6",
  CAM_TOO_CLOSE : "7",
  CAM_MIN_HORIZONTAL : "8",
  AUTO_TIME : "9",
  IMU_TRANS_ACCEL_THRESH_X : "10",
  IMU_TRANS_ACCEL_THRESH_Y : "11",
  IMU_TRANS_ACCEL_THRESH_Z : "12",
  IMU_ROT_ACCEL_THRESH_X : "13",
  IMU_ROT_ACCEL_THRESH_Y : "14",
  IMU_ROT_ACCEL_THRESH_Z : "15",
  IMU_ROT_MOVE_THRESH_X : "16",
  IMU_ROT_MOVE_THRESH_Y : "17",
  IMU_ROT_MOVE_THRESH_Z : "18",
  IMU_TRANS_MOVE_THRESH_X : "19",
  IMU_TRANS_MOVE_THRESH_Y : "20",
  IMU_TRANS_MOVE_THRESH_Z : "21",

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
