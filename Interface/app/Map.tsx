'use client';
import { relative } from 'path';
import './globals.css'

export default function Compass({x=0,y=0}: any) { 
  
  const WIDTH = 400
  const HEIGHT = 400

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

      </div>
    </div>
  );
}