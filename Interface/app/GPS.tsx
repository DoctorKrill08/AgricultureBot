'use client';
import { stat } from 'fs';
import './globals.css'
import './interface_map'
import { INCHES_PER_NODE, MapKey, Command } from './interface_map';
import React, { useRef, useState } from 'react';
import path from 'path';


const DEFAULT_ZOOM = 50

export default function GPS({gpsData}: any) { 
  const [s3rw, wwwa] = useState(0);
  return (
    
    <div>
      <h1 className='big-text' style={{
        marginTop: 100
      }}>
        GPS
      </h1>
        {gpsData}
    </div>
  );
}