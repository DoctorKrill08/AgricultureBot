'use client';
import { relative } from 'path';
import './globals.css'
import React, { useRef, useState } from 'react';



export default function Map({bx=0,by=0,tx=0,ty=0,bYaw=0,tYaw=0, onMove}: any) { 

  bYaw *= -1
  tYaw *= -1
  const PIXELS_PER_INCH = 3

  bx *= PIXELS_PER_INCH
  by *= -PIXELS_PER_INCH
  tx *= PIXELS_PER_INCH
  ty *= -PIXELS_PER_INCH
  
  const WIDTH = 800
  const HEIGHT = 800

  const POINT_RADIUS = 10

  var botX = (WIDTH / 2) - (POINT_RADIUS / 2) + bx
  var botY = (HEIGHT / 2) - (POINT_RADIUS /2 ) + by

  var tarX = (WIDTH / 2) - (POINT_RADIUS / 2) + tx
  var tarY = (HEIGHT / 2) - (POINT_RADIUS /2 ) + ty

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
            left : String(botX) + 'px',
            top: String(botY) + 'px',
            backgroundColor: 'red',
            rotate: String(bYaw) + 'rad'
        }}/>

        <div className='map-point' style={{
            width : String(POINT_RADIUS) + 'px',
            height : String(POINT_RADIUS) + 'px',
            left : String(tarX) + 'px',
            top: String(tarY) + 'px',
            backgroundColor: 'green',
            rotate: String(tYaw) + 'rad'
        }}/>

      </div>
    </div>
  );
}