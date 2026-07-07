'use client';
import { relative } from 'path';
import './globals.css'
import React, { useRef, useState } from 'react';


type MapProps = {
  onMove: (x: number, y: number) => void;
};

export default function Compass({bx=0,by=0,tx=0,ty=0, onMove}: any) { 
  
  const PIXELS_PER_INCH = 2

  bx *= PIXELS_PER_INCH
  by *= PIXELS_PER_INCH
  tx *= PIXELS_PER_INCH
  ty *= PIXELS_PER_INCH
  
  const WIDTH = 600
  const HEIGHT = 600

  const POINT_RADIUS = 10

  var botX = (WIDTH / 2) - (POINT_RADIUS / 2) + bx
  var botY = (HEIGHT / 2) + (POINT_RADIUS /2 ) - by

  var tarX = (WIDTH / 2) - (POINT_RADIUS / 2) + tx
  var tarY = (HEIGHT / 2) + (POINT_RADIUS /2 ) - ty

  const [position, setPosition] = useState({ x: 0, y: 0 });
  const handleMouseDown = (event: React.MouseEvent) => {
    var x = event.clientX
    var y = event.clientY
    console.log("x: ", x, " y: ",y)
    x -= (WIDTH / 2)
    y -= (HEIGHT / 2)

    x /= PIXELS_PER_INCH
    y /= PIXELS_PER_INCH
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
      <div className='map-box' style={{
        width : String(WIDTH) + 'px',
        height: String(HEIGHT) + 'px'
      }}>
          <div className='map-point' style={{
            width : String(POINT_RADIUS) + 'px',
            height : String(POINT_RADIUS) + 'px',
            left : String(botX) + 'px',
            top: String(botY) + 'px',
            backgroundColor: 'red'
        }}/>

        <div className='map-point' style={{
            width : String(POINT_RADIUS) + 'px',
            height : String(POINT_RADIUS) + 'px',
            left : String(tarX) + 'px',
            top: String(tarY) + 'px',
            backgroundColor: 'green'
        }}/>

      </div>
    </div>
  );
}