'use client';
import { relative } from 'path';
import './globals.css'

export default function Compass({yaw}: any) { 
  yaw -= Math.PI / 2
  const RADIUS = 200

  const POINTER_HEIGHT = 20
  const POINTER_WIDTH = RADIUS / 2

  const INNER_RADIUS = 30
  const TEXT_HEIGHT = 40

  var top = ((RADIUS / 2) - (POINTER_HEIGHT / 2) * Math.cos(yaw))
  var left = (POINTER_WIDTH) + ((POINTER_HEIGHT/2 )* Math.sin(yaw))
  

  return (
    <div style={{
        width: '300px',
        height: '300px',
      }}>
      <h1 className='big-text'>
        COMPASS
      </h1>
        <div className='compass-outer' style={{
          height: String(RADIUS) + 'px',
          width: String(RADIUS) + 'px'
        }}>
          <h1 className='compass-text' style={{
            height: String(TEXT_HEIGHT) + 'px',
            fontSize: String(TEXT_HEIGHT) + 'px',
            width: String(TEXT_HEIGHT) + 'px',
            top: String(-TEXT_HEIGHT) + 'px',
            left: String((RADIUS/2) - (TEXT_HEIGHT / 2)) + 'px'
          }}>
            N
          </h1>
          <h1 className='compass-text' style={{
            height: String(TEXT_HEIGHT) + 'px',
            fontSize: String(TEXT_HEIGHT) + 'px',
            width: String(TEXT_HEIGHT) + 'px',
            bottom: String(-TEXT_HEIGHT) + 'px',
            left: String((RADIUS/2) - (TEXT_HEIGHT / 2)) + 'px'
          }}>
            S
          </h1>
          <h1 className='compass-text' style={{
            width: String(TEXT_HEIGHT) + 'px',
            height: String(TEXT_HEIGHT) + 'px',
            fontSize: String(TEXT_HEIGHT) + 'px',
            top: String((RADIUS/2) - (TEXT_HEIGHT + TEXT_HEIGHT/4)) + 'px',
            right: String(-(TEXT_HEIGHT / 2)) + 'px'
          }}>
            E
          </h1>
          <h1 className='compass-text' style={{
            width: String(TEXT_HEIGHT) + 'px',
            height: String(TEXT_HEIGHT) + 'px',
            fontSize: String(TEXT_HEIGHT) + 'px',
            top: String((RADIUS/2) - (TEXT_HEIGHT + TEXT_HEIGHT/4)) + 'px',
            left: String(-(TEXT_HEIGHT / 2)) + 'px'
          }}>
            W
          </h1>
          <div className='compass-inner' style={{
                height : String(INNER_RADIUS) + 'px',
                width : String(INNER_RADIUS) + 'px',
                top: String((RADIUS/2) - INNER_RADIUS/2) + 'px',
                left: String((RADIUS/2) - INNER_RADIUS/2) + 'px',
                zIndex: 15
                
              }}/>
              <div className='compass-pointer' style={{
                height : String(POINTER_HEIGHT) + 'px',
                width : String(POINTER_WIDTH) + 'px',
                top: String(top) + 'px',
                left: String(left) + 'px',
                rotate: String(yaw) + "rad",
                
              }}/>
        </div>
      </div>
  );
}