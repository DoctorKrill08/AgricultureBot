'use client';
import './globals.css'
import './interface_map'
import { INCHES_PER_NODE } from './interface_map';
import React, { useRef, useState } from 'react';

/*const [xOffset, setXOffset] = useState(0);
const [yOffset, setYOffset] = useState(0);
const [zoom, setZoom] = useState(1);*/


const PIXELS_PER_INCH = 3
const WIDTH = 400
const HEIGHT = 400
const POINT_RADIUS = PIXELS_PER_INCH * 10
const OBSTACLE_RADIUS = PIXELS_PER_INCH * Number(INCHES_PER_NODE)

const MAX_ZOOM_OUT = 0.125
const MAX_ZOOM_IN = 4

const WEST = "W"
const EAST = "E"
const NORTH = "N"
const SOUTH = "S"

const MAP_OFFSET_INCREMENT = 0.1 //Proportion of map size

var pixelsPerInch = PIXELS_PER_INCH

export default function Map({bx=0,by=0,tx=0,ty=0,bYaw=0,tYaw=0,vx=0,vy=0, map_data, onMove}: any) { 
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


  function realToMap(x : number,y : number,yaw : number, radius : number){
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

  function parseMap(map_data: string){
    obstacles = []
    if (map_data == null || map_data == ""){
      console.log("No map data")
      return
    }
    var points = map_data.split('/'); //Array of Strings
    for (let i = 0; i < points.length; i++){
      let point = points[i].split(","); //Array of strings, x and y
      let x = Number(point[0])
      let y = Number(point[1])
      let status = String(point[2])
      let translated = realToMap(x,y,0,POINT_RADIUS);
      x = translated[0]
      y = translated[1]
      obstacles[i] = [x,y,status]
    }
    
  }
  function statusToColor(status: any){
    if (status == "O"){
      return 'maroon'
    }
    if (status == 'S'){
      return 'orange'
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
  var netPose = realToMap(vx,vy,0,obstacleRadius)
  vx = netPose[0]
  vy = netPose[1]

  var botPose = realToMap(bx,by,bYaw,pointRadius)
  bx = botPose[0]
  by = botPose[1]
  bYaw = botPose[2]

  var tarPose = realToMap(tx,ty,tYaw,pointRadius)
  tx = tarPose[0]
  ty = tarPose[1]
  tYaw = tarPose[2]

  parseMap(map_data)

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
          
          width : '100%',
          height: '100%',
          backgroundColor: '#ff000000',
          backgroundImage: "linear-gradient(to right, " + color + " " + size + "px, transparent " + size + "px),linear-gradient(to bottom, "+ color + " " + size + "px, transparent "+ size + "px)",
          backgroundSize: String(calculateGridSize(inches)) + 'px '+ String(calculateGridSize(inches)) + 'px' 
        }}/>
      )
  }
  const handleMouseDown = (event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();

    var x = event.clientX - rect.left
    var y = event.clientY - rect.top
    console.log("x: ", x, " y: ",y)
    let translated = mapToReal(x,y)
    x = translated[0]
    y = translated[1]
    console.log("translated x: ", x, " translated y: ",y)
    onMove(x, y);
  };

  const handleMouseHover = (event : React.MouseEvent) => {
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
      <div className='map-box'
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseHover}
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
            rotate: String(bYaw) + 'rad'
        }}/>

        <div className='map-point' style={{
            width : String(pointRadius) + 'px',
            height : String(pointRadius) + 'px',
            left : String(tx) + 'px',
            top: String(ty) + 'px',
            backgroundColor: 'yellow',
            rotate: String(tYaw) + 'rad',
            borderWidth: 0
        }}/>

        <div className='map-point' style={{
            width : String(obstacleRadius) + 'px',
            height : String(obstacleRadius) + 'px',
            left : String(vx) + 'px',
            top: String(vy) + 'px',
            backgroundColor: 'purple',
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