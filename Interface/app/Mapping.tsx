'use client';
import { stat } from 'fs';
import './globals.css'
import './interface_map'
import { INCHES_PER_NODE, MapKey, Command } from './interface_map';
import React, { useRef, useState } from 'react';
import path from 'path';


const PIXELS_PER_INCH = 4
const WIDTH = 300
const HEIGHT = 300
const POINT_RADIUS = PIXELS_PER_INCH * 10
const OBSTACLE_RADIUS = PIXELS_PER_INCH * Number(INCHES_PER_NODE)

const MAX_ZOOM_OUT = 0.125
const MAX_ZOOM_IN = 2

const WEST = "W"
const EAST = "E"
const NORTH = "N"
const SOUTH = "S"

export const DELETE_PATH = Command.DELETE_PATH
export const DELETE_ALL_PATHS = Command.DELETE_ALL_PATHS
export const ADD_PATH = Command.ADD_PATH

const MAP_OFFSET_INCREMENT = 0.1 //Proportion of map size

var pixelsPerInch = PIXELS_PER_INCH

export default function Mapping({bx=0,by=0,bYaw=0,vx=0,vy=0, mapData, pathData, mapCommand}: any) { 
  let botXInches = bx
  let botYInches = by
  const [xOffset, setXOffset] = useState(0);
  const [yOffset, setYOffset] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [hoverX, setHoverX] = useState(0);
  const [hoverY, setHoverY] = useState(0);

  const handeZoom = (direction : number) => {
    if (direction == -1){
      if (zoom / 2 >= MAX_ZOOM_OUT){
        setZoom(zoom / 2)
      }
    }else{
      if (zoom * 2 <= MAX_ZOOM_IN){
        setZoom(zoom * 2)
      }
    }
  };
  const handleMapMove = (direction : string) => {
    let increment = Math.round(mapToReal((WIDTH / 2) + (MAP_OFFSET_INCREMENT * (WIDTH / 2)),0,true)[0])
    if (direction == WEST){
      setXOffset(xOffset - increment)
      return
    }
    if (direction == EAST){
      setXOffset(xOffset + increment)
      return
    }
    if (direction == NORTH){
      setYOffset(yOffset + increment)
      return
    }
    if (direction == SOUTH){
      setYOffset(yOffset - increment)
      return
    }
  };

  function zoomToPoint(ZOOM : number = 1, X : number = 0, Y : number = 0){
    setZoom(ZOOM)
    setXOffset(X)
    setYOffset(Y)
  }
  function realToMap(x : number,y : number,yaw : number){
    x -= xOffset
    y -= yOffset

    yaw *= -1
    x *= pixelsPerInch
    y *= -pixelsPerInch

    x = (WIDTH / 2) + x
    y = (HEIGHT / 2) + y

    x = Math.round(x)
    y = Math.round(y)
    return [x,y,yaw]
  }
  function mapToReal(x : number,y : number, ignore_offset : boolean = false){
    x -= ((WIDTH / 2))
    y -= ((HEIGHT / 2))

    x /= pixelsPerInch
    y /= -pixelsPerInch

    if (!ignore_offset){
      x += xOffset
      y += yOffset
    }
    return [x,y]
  }

  var obstacles : any[][] = []
  var pathPoints : any[][] = []

  function parseMap(mapData: string){
    obstacles = []
    if (mapData == null || mapData == ""){
      console.log("No map data")
      return
    }
    var points = mapData.split('/'); //Array of Strings
    for (let i = 0; i < points.length; i++){
      let point = points[i].split(","); //Array of strings, x and y
      let x = Number(point[0])
      let y = Number(point[1])
      let status = String(point[2])
      let translated = realToMap(x,y,0);
      x = translated[0]
      y = translated[1]
      obstacles[i] = [x,y,status]
    }
  }
  
  function statusToColor(status: any){
    if (status == MapKey.OBSTACLE){
      return 'maroon'
    }
    if (status == MapKey.SAVED_OBSTACLE){
      return 'orange'
    }
    if (status == MapKey.CURRENT_PATH){
      return 'lime'
    }
    if (status == MapKey.PATH_IN_QUE){
      return 'yellow'
    }
    return 'white'
  }

  function obstaclesToDiv(){
      if (obstacles.length == 0){
        return
      }
      return (
      <div id="container">
        {obstacles.map((item, index) => (
          <div key={index} className="map-point" style={{
              width : String(obstacleRadius) + 'px',
              height : String(obstacleRadius) + 'px',
              left : String(item[0]) + 'px',
              top: String(item[1]) + 'px',
              pointerEvents: 'none',
              backgroundColor: statusToColor(item[2]),
              borderWidth: 0
          }}/>
        ))}
      </div>
    );
      
    }

  function vector_to_div(bx: number, by: number, vx : number,vy : number, color : string){
    let delta_x = vx - bx
    let delta_y = vy - by
    let thickness = 5 * pixelsPerInch
    if (thickness < 4){
      thickness = 4
    }
    if (thickness > 20){
      thickness = 20
    }
    let distance = Math.sqrt((Math.pow(delta_x,2) + Math.pow(delta_y,2)))
    let angle = Math.atan2(delta_y,delta_x)
    let TOP = by - ((thickness / 2) * Math.cos(angle)) + 'px'
    let LEFT = bx + ((thickness / 2) * Math.sin(angle)) + 'px'
    pixelsPerInch = PIXELS_PER_INCH * zoom
    return (
      //Bar
      <div style={{
          backgroundColor: color,
          position: 'absolute',
          rotate: String(angle) + 'rad',
          transformOrigin: 'top left',
          zIndex: 101,
          top: TOP,
          pointerEvents: 'none',
          left: LEFT,
          width: String(distance) + 'px',
          height: String(thickness) + 'px',
      }}/>
    )

  }
  var obstacleRadius = OBSTACLE_RADIUS * zoom
  var pointRadius = POINT_RADIUS * zoom
  if (obstacleRadius < 1){
    obstacleRadius = 1
  }
  if (pointRadius < 1){
    pointRadius = 1
  }
  
  vx += bx
  vy += by
  var netPose = realToMap(vx,vy,0)
  vx = netPose[0]
  vy = netPose[1]

  var botPose = realToMap(bx,by,bYaw)
  bx = botPose[0]
  by = botPose[1]
  bYaw = botPose[2]

  function generatePaths(){
    pathPoints = []
    if (pathData == null || pathData == ""){
      console.log("no path data")
      return
    }
    var points = pathData.split('/'); //Array of Strings
    for (let i = 0; i < points.length; i++){
      if (points[i].length < 2){
        continue
      }
      let point = points[i].split(',')
      let tx = point[0]
      let ty = point[1]
      let tYaw = point[3]
      let status = point[2]
      var tarPose = realToMap(tx,ty,tYaw)
      pathPoints[i] = [tarPose[0],tarPose[1],status,tarPose[2]]
    }
    if (pathPoints.length == 0){
      return
    }
     return (
      <div id="container">
        {pathPoints.map((item, index) => (
          <div key={index} className="map-point" style={{
              width : String(pointRadius) + 'px',
              height : String(pointRadius) + 'px',
              left : String(item[0]) + 'px',
              top: String(item[1]) + 'px',
              backgroundColor: statusToColor(item[2]),
              borderWidth: 0
          }} onClick={(e) => mapCommand(e,index,0,0,DELETE_PATH)}/>
        ))}
      </div>
    );
    
  }

  parseMap(mapData)

  function calculateGridSize(inches : number){
    let size = pixelsPerInch * inches
    if (size < 8){
      return 0
    }
    if (size > 200){
      return 0
    }
    return size
  }
  function createGrid(inches : number, color : string, size : number){
      return (
        <div className='map-box-overlay'
        style={{
          position: 'absolute',
          pointerEvents: 'none',
          width : '100%',
          height: '100%',
          backgroundColor: '#ff000000',
          backgroundImage: "linear-gradient(to right, " + color + " " + size + "px, transparent " + size + "px),linear-gradient(to bottom, "+ color + " " + size + "px, transparent "+ size + "px)",
          backgroundSize: String(calculateGridSize(inches)) + 'px '+ String(calculateGridSize(inches)) + 'px' 
        }}/>
      )
  }
  const handleMapClicked = (event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();

    var x = event.clientX - rect.left
    var y = event.clientY - rect.top
    console.log("x: ", x, " y: ",y)
    let translated = mapToReal(x,y)
    x = translated[0]
    y = translated[1]
    let yaw = 0
    console.log("translated x: ", x, " translated y: ",y)
    mapCommand(event,x, y,yaw,ADD_PATH);
  };

  const handleMapHover = (event : React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();

    var x = event.clientX - rect.left
    var y = event.clientY - rect.top
    console.log("x: ", x, " y: ",y)
    let translated = mapToReal(x,y)
    x = translated[0]
    y = translated[1]
    setHoverX(x)
    setHoverY(y)
  }

  return (
    
    <div>
      <h1 className='big-text' style={{
        marginTop: 100
      }}>
        MAP
      </h1>

      <button className='button' 
      onClick={(e) => mapCommand(e,0,0,0,DELETE_ALL_PATHS,true)}>
        <h2 style={{color : 'red'}}>DELETE ALL PATHS</h2>
      </button>
      <br/>
      <br/>

      <div className='map-box'
      onMouseDown={handleMapClicked}
      onMouseMove={handleMapHover}
      style={{
        width : String(WIDTH) + 'px',
        height: String(HEIGHT) + 'px',
        backgroundColor: '#111',
      }}>
        
        {createGrid(1,'#7e7e7e54',1)}
        {createGrid(12,'#00ff0d4b',3)}
        {createGrid(36,'#2f009e9c',5)}
          <div className='map-point' style={{
            width : String(pointRadius) + 'px',
            height : String(pointRadius) + 'px',
            left : String(bx) + 'px',
            top: String(by) + 'px',
            backgroundColor: 'blue',
            borderRightColor: 'purple',
            borderRightWidth: '4px',
            pointerEvents: 'none',
            rotate: String(bYaw) + 'rad'
        }}/>

        {generatePaths()}

        <div className='map-point' style={{
            width : String(obstacleRadius) + 'px',
            height : String(obstacleRadius) + 'px',
            left : String(vx) + 'px',
            top: String(vy) + 'px',
            backgroundColor: 'purple',
            pointerEvents: 'none',
            zIndex: 100,
            rotate: String(0) + 'rad'
        }}/>
        {vector_to_div(bx,by,vx,vy,'purple')}


        {obstaclesToDiv()}
      </div>
      <p style={{fontSize : 20}}>
      Zoom: <b>%{zoom * 100}</b>, X-Offset: {xOffset} inches, Y-Offset: {yOffset} inches, Mouse World Pos: {hoverX},{hoverY}
      </p>
      <button className='button' 
      onClick={() => handeZoom(-1)}>
        <h2 style={{color : 'red'}}>
          Zoom  Out
        </h2>
      </button>
      <button className='button'
        onClick={() => handeZoom(1)}>
        <h2 style={{color : 'lime'}}>
          Zoom  In
        </h2>
      </button>
      {/* DIRECTIONS!!!!! */}
      <button className='button'
        onClick={() => handleMapMove(WEST)}>
        <h2>← WEST</h2>
      </button>
      <button className='button'
        onClick={() => handleMapMove(EAST)}>
        <h2>→ EAST</h2>
      </button>
      <button className='button'
        onClick={() => handleMapMove(NORTH)}>
        <h2>↑ NORTH</h2>
      </button>
      <button className='button'
        onClick={() => handleMapMove(SOUTH)}>
        <h2>↓ SOUTH</h2>
      </button>
      <button className='button'
        onClick={() => zoomToPoint()}>
        <h2>TO HOME</h2>
      </button>
      <button className='button'
        onClick={() => zoomToPoint(1,botXInches,botYInches)}>
        <h2>TO ROBOT</h2>
      </button>
      <p style={{fontSize: 20, color : 'blue'}}>Blue = Yard</p>
      <p style={{fontSize: 20, color : 'green'}}>Green = Foot</p>
      <p style={{fontSize: 20, color : 'white'}}>White = Inch</p>
      <br/>
    </div>
  );
}