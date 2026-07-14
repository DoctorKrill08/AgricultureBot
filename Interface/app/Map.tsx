'use client';
import { parse, relative } from 'path';
import './globals.css'
import React, { useRef, useState } from 'react';

const PIXELS_PER_INCH = 3
const WIDTH = 800
const HEIGHT = 800
const POINT_RADIUS = 10
const OBSTACLE_RADIUS = 2

function realToMap(x : number,y : number,yaw : number, radius : number){
  yaw *= -1
  x *= PIXELS_PER_INCH
  y *= -PIXELS_PER_INCH

  x = (WIDTH / 2) - (radius / 2) + x
  y = (HEIGHT / 2) - (radius / 2) + y
  return [x,y,yaw]
}
var obstacles : number[][] = []

function parseMap(map_data: string){
  obstacles = []
  var points = map_data.split('/'); //Array of Strings
  for (let i = 0; i < points.length; i++){
    let point = points[i].split(","); //Array of strings, x and y
    let x = Number(point[0])
    let y = Number(point[1])
    let translated = realToMap(x,y,0,POINT_RADIUS);
    x = translated[0]
    y = translated[1]
    obstacles[i] = [x,y]
  }
  
}
function obstaclesToDiv(){
  const container = document.getElementById('obstalces');
  if (container == null){
    console.log("CONTAINER IS NULL")
    return
  }
  //Clear children
  container.replaceChildren()

  for (let i = 0; i < obstacles.length; i++){
    const div = document.createElement('div');

    let x = obstacles[i][0]
    let y = obstacles[i][1]

    div.className = 'map-point';
    div.id = 'obstacle-point';
    div.style.backgroundColor = 'red';
    div.style.width = String(OBSTACLE_RADIUS) + 'px'
    div.style.height = String(OBSTACLE_RADIUS) + 'px'
    div.style.left = String(x) + 'px'
    div.style.top = String(y) + 'px'
    container.appendChild(div); 
  }
}

export default function Map({bx=0,by=0,tx=0,ty=0,bYaw=0,tYaw=0, map_data, onMove}: any) { 

  var botPose = realToMap(bx,by,bYaw,POINT_RADIUS)
  bx = botPose[0]
  by = botPose[1]
  bYaw = botPose[2]

  var tarPose = realToMap(tx,ty,tYaw,POINT_RADIUS)
  tx = tarPose[0]
  ty = tarPose[1]
  tYaw = tarPose[2]

  parseMap(map_data)
  obstaclesToDiv()

  //const [position, setPosition] = useState({ x: 0, y: 0 });
  const handleMouseDown = (event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();

    var x = event.clientX - rect.left
    var y = event.clientY - rect.top
    console.log("x: ", x, " y: ",y)
    
    x -= (WIDTH / 2)
    y -= (HEIGHT / 2)

    x -= POINT_RADIUS/2
    y -= POINT_RADIUS

    x /= PIXELS_PER_INCH
    y /= -PIXELS_PER_INCH
    console.log("translated x: ", x, " translated y: ",y)

    onMove(x, y);
  };

  return (
    
    <div>
      <h1 className='big-text' style={{
        marginTop: 100
      }}>
        MAP
      </h1>
      <div className='map-box'
      onMouseDown={handleMouseDown}
      style={{
        width : String(WIDTH) + 'px',
        height: String(HEIGHT) + 'px'
      }}>
          <div className='map-point' style={{
            width : String(POINT_RADIUS) + 'px',
            height : String(POINT_RADIUS) + 'px',
            left : String(bx) + 'px',
            top: String(by) + 'px',
            backgroundColor: 'blue',
            rotate: String(bYaw) + 'rad'
        }}/>

        <div className='map-point' style={{
            width : String(POINT_RADIUS) + 'px',
            height : String(POINT_RADIUS) + 'px',
            left : String(tx) + 'px',
            top: String(ty) + 'px',
            backgroundColor: 'yellow',
            rotate: String(tYaw) + 'rad'
        }}/>
        <div id='obstacles'/>
      </div>

    </div>
  );
}