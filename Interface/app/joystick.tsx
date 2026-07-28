'use client';

import React, {useEffect,useRef, useState } from 'react';
import './globals.css'

type JoystickProps = {
  onMove: (x: number, y: number) => void;
};

export default function Joystick({ onMove }: JoystickProps) {
  const requestRef = useRef<number | null>(null);
  const [gamepadConnected,setGamepadConnected] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [prev_position, setPrevPosition] = useState({ x: 0, y: 0 });

   useEffect(() => {    
    // 1. If not connected yet, stop here. 
    // When gamepadConnected changes to true, this entire effect will re-run!
    if (!gamepadConnected) {
      return; 
    }

    const DEADZONE = 0.15;

    const pollGamepad = () => {
      const gamepads = navigator.getGamepads();
      const activeGamepad = Array.from(gamepads).find(gp => gp !== null);
      
      if (activeGamepad && activeGamepad.axes.length >= 2) {
        let x = activeGamepad.axes[2];
        let y = activeGamepad.axes[1];

        if (Math.abs(x) < DEADZONE) x = 0;
        if (Math.abs(y) < DEADZONE) y = 0;
        
        // Note: Make sure updatePosition is defined or changed to onMove
        
        updatePosition(
          x,
          y
        );
      }
      
      requestRef.current = requestAnimationFrame(pollGamepad);
    };

    requestRef.current = requestAnimationFrame(pollGamepad);

    return () => {
      if (requestRef.current) {
        console.log("Cleaning up animation frame");
        cancelAnimationFrame(requestRef.current);
      }
    };
    
  // 2. CRITICAL FIX: Add gamepadConnected here
  }, [gamepadConnected]); 


  const joystickRef = useRef<HTMLDivElement>(null);

  const [dragging, setDragging] = useState(false);

  const radius = 100;      // Outer joystick radius
  const knobRadius = 30;   // Inner knob radius

  const updatePosition = (clientX: number, clientY: number) => {
    if (gamepadConnected){
      let x = clientX
      let y = clientY
      onMove(x,y)
      const maxDistance = radius - knobRadius;
      let distance = Math.sqrt(Math.pow(x,2) + Math.pow(y,2)) * maxDistance
      if (distance <= 0){
        x = 0
        y = 0
        setPosition({ x, y })
      }

      const angle = Math.atan2(y, x);

      x = Math.cos(angle) * distance;
      y = Math.sin(angle) * distance;
      setPosition({ x, y })
      return
    }
    if (!joystickRef.current) return;

    const rect = joystickRef.current.getBoundingClientRect();

    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    let x = clientX - centerX;
    let y = clientY - centerY;

    const distance = Math.sqrt(x * x + y * y);

    const maxDistance = radius - knobRadius;

    if (distance > maxDistance) {
      const angle = Math.atan2(y, x);

      x = Math.cos(angle) * maxDistance;
      y = Math.sin(angle) * maxDistance;
    }

    setPosition({ x, y });

    // Normalized values (-1 to 1)
    const normalizedX = x / maxDistance;
    const normalizedY = -y / maxDistance;

    console.log({
      x: normalizedX.toFixed(2),
      y: normalizedY.toFixed(2),
    });

    onMove(normalizedX, normalizedY);
    
  };

  const handleMouseDown = (event: React.MouseEvent) => {
    if (gamepadConnected){
      return
    }
    setDragging(true);
    updatePosition(event.clientX, event.clientY);
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    if (gamepadConnected){
      return
    }
    if (!dragging) return;

    updatePosition(event.clientX, event.clientY);
  };

  const handleMouseUp = () => {
    if (gamepadConnected){
      return
    }
    setDragging(false);

    // Return to center
    setPosition({ x: 0, y: 0 });
    onMove(0, 0);
  };

  const handleTouchStart = (event: React.TouchEvent) => {
    if (gamepadConnected){
      return
    }
    setDragging(true);

    const touch = event.touches[0];
    updatePosition(touch.clientX, touch.clientY);
  };

  const handleTouchMove = (event: React.TouchEvent) => {
    if (gamepadConnected){
      return
    }
    if (!dragging) return;

    const touch = event.touches[0];
    updatePosition(touch.clientX, touch.clientY);
  };

  const handleTouchEnd = () => {
    if (gamepadConnected){
      return
    }
    setDragging(false);
    setPosition({ x: 0, y: 0 });
    onMove(0, 0);
  };

  return (
    <div
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{
        width: '400px',
        height: '700px',
      }}
      
    >
      <h1 className='big-text'>
        JOYSTICK
      </h1>
      <button className='button' onClick={() => setGamepadConnected(!gamepadConnected)}>
        Controller Mode: {String(gamepadConnected)}
      </button>
      <br/>
      <br/>
      <div
        ref={joystickRef}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
        style={{
          position: 'relative',
          width: radius * 2,
          height: radius * 2,
          borderRadius: '50%',
          border: '3px solid #666',
          background: '#ddd',
          margin: '50px',
          touchAction: 'none',
        }}
      >
        <div
          style={{
            position: 'absolute',
            width: knobRadius * 2,
            height: knobRadius * 2,
            borderRadius: '50%',
            background: '#444',

            left: '50%',
            top: '50%',

            transform: `translate(calc(-50% + ${position.x}px), calc(-50% + ${position.y}px))`,
          }}
        />
      </div>

      <div style={{ marginLeft: 50 }}>
        <h3>Coordinates</h3>
        <p>X: {(position.x / (radius - knobRadius)).toFixed(2)}</p>
        <p>Y: {(-position.y / (radius - knobRadius)).toFixed(2)}</p>
      </div>
    </div>
  );
}