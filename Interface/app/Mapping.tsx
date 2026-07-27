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

const MAP_OFFSET_INCREMENT = 0.1 //Proportion of map size

var pixelsPerInch = PIXELS_PER_INCH

export default function Mapping({bx=0,by=0,bYaw=0,vx=0,vy=0, mapData, pathData, sendCommand}: any) { 
  function handleMouseMapCommands(event : any, command : string, value : string, bypass : boolean = false){
     if (event.target != event.currentTarget && ! bypass){
      console.log(command," failed")
      return
    }
    sendCommand(command,value)
  }
  const handleInputMapCommands = (command : string, value : string) => (event : React.KeyboardEvent<HTMLInputElement>) => {
     if (event.key === 'Enter') {
      event.preventDefault(); 
      var input = parseFloat((event.target as HTMLInputElement).value);
      if (Number.isNaN(input)){
        return
      }
      value += (',' + String(input))
      sendCommand(command,value)
    }
  }


  let botXInches = bx
  let botYInches = by
  const [xOffset, setXOffset] = useState(0);
  const [yOffset, setYOffset] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [hoverX, setHoverX] = useState(0);
  const [hoverY, setHoverY] = useState(0);
  const [selectedPoint, setSelectedPoint] = useState(0);

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

  //Parse Paths:
  function parsePaths(){
    if (pathData == null || pathData == ""){
      return
    }
    var points = pathData.split('/'); //Array of Strings
    for (let i = 0; i < points.length; i++){
      if (points[i].length < 2){
        continue
      }
      let point = points[i].split(',')
      let xInches = point[0]
      let yInches = point[1]
      let yaw = point[3]
      let status = point[2]
      var tarPose = realToMap(xInches,yInches,yaw)
      let xPixels = tarPose[0]
      let yPixels = tarPose[1]
      let angle = tarPose[2]
      pathPoints[i] = [xPixels,yPixels,status,angle,xInches,yInches,yaw]
    }
  }
  parsePaths()
  function visualizePaths(){
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
              borderWidth: 0,
              fontWeight: 'bold',
              fontSize: '24px',
              justifyContent: 'center',
              alignItems: 'center',
              display: 'flex',
              WebkitTextStroke: '1.3px black',
              rotate : (item[3]) + 'rad',
              color: 'white'
          }} onClick={(e) => setSelectedPoint(index)}>
            {index}
            </div>
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
    console.log("translated x: ", x, " translated y: ",y)
    setSelectedPoint(pathPoints.length)
    handleMouseMapCommands(event,Command.ADD_PATH,`${x},${y}`);
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

  function displaySelectedPoint(){
    let HEIGHT = '150px'
    let containerTemplate = <div style={{width: '100px',height: HEIGHT}}/>
    if (selectedPoint < 0){
      return containerTemplate
    }
    if (pathPoints.length < 0){
      return containerTemplate
    }
    let path = pathPoints[selectedPoint]
    if (path == null){
      return containerTemplate
    }
    if (path.length == 0){
      return containerTemplate
    }

    let xPixels = path[0]
    let yPixels = path[1]
    let status = path[2]
    let angle = path[3]
    let xInches = path[4]
    let yInches = path[5]
    let yaw = path[6]
    return(
      <div style={{color: 'white', width: '100%', height: HEIGHT}}>
          Selected Point: {selectedPoint} <br/>
          X: {path[0]} pixels, {xInches} inches <br/>
          Y: {path[1]} pixels, {yInches} inches <br/>
          Angle (client): {angle * (180 / Math.PI)} degrees, Yaw (robot): {yaw * (180 / Math.PI)} degrees <br/>
          <br/>
          <button className='button' onMouseUp={(e) => handleMouseMapCommands(e,Command.DELETE_PATH,String(selectedPoint))} style={{
            color: 'red'
          }}>
            DELETE POINT
          </button>
          SET YAW: 
          <input enterKeyHint="done" type = "number" className="button" defaultValue={yaw} placeholder='...' onKeyDown={handleInputMapCommands(Command.SET_PATH_YAW,String(selectedPoint))}/> 
          SET INDEX: 
          <input enterKeyHint="done" type = "number" className="button" defaultValue={0} placeholder='...' onKeyDown={handleInputMapCommands(Command.SET_PATH_INDEX,String(selectedPoint))}/> 
      </div>
    )
  }

  return (
    
    <div>
      <h1 className='big-text' style={{
        marginTop: 100
      }}>
        MAP
      </h1>
      Click on map to add a point
      <br/>
      Click on a point to get options to edit or delete
      <br/><br/>
      <button className='button' 
      onClick={(e) => handleMouseMapCommands(e,Command.DELETE_ALL_PATHS,'0')}>
        <p style={{color : 'red'}}>DELETE ALL PATHS</p>
      </button>
      <br/><br/>
      {displaySelectedPoint()}
      <br/><br/>
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

        {visualizePaths()}

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
      <p>
      Zoom: <b>%{zoom * 100}</b>, X-Offset: {xOffset} inches, Y-Offset: {yOffset} inches, Mouse World Pos: {hoverX},{hoverY}
      </p>
      <button className='button' 
      onClick={() => handeZoom(-1)}>
        <p style={{color : 'red'}}>
          Zoom  Out
        </p>
      </button>
      <button className='button'
        onClick={() => handeZoom(1)}>
        <p style={{color : 'lime'}}>
          Zoom  In
        </p>
      </button>
      {/* DIRECTIONS!!!!! */}
      <button className='button'
        onClick={() => handleMapMove(WEST)}>
        <p>← WEST</p>
      </button>
      <button className='button'
        onClick={() => handleMapMove(EAST)}>
        <p>→ EAST</p>
      </button>
      <button className='button'
        onClick={() => handleMapMove(NORTH)}>
        <p>↑ NORTH</p>
      </button>
      <button className='button'
        onClick={() => handleMapMove(SOUTH)}>
        <p>↓ SOUTH</p>
      </button>
      <button className='button'
        onClick={() => zoomToPoint()}>
        <p>TO HOME</p>
      </button>
      <button className='button'
        onClick={() => zoomToPoint(1,botXInches,botYInches)}>
        <p>TO ROBOT</p>
      </button>
      <p style={{color : 'blue'}}>Blue = Yard</p>
      <p style={{color : 'green'}}>Green = Foot</p>
      <p style={{color : 'white'}}>White = Inch</p>
      <br/>
    </div>
  );
}