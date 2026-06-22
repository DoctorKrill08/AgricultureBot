'use client';

import React, { useRef, useState } from 'react';

type JoystickProps = {
  onMove: (x: number, y: number) => void;
};

export default function Joystick({ onMove }: JoystickProps) {
  const joystickRef = useRef<HTMLDivElement>(null);

  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);

  const radius = 100;      // Outer joystick radius
  const knobRadius = 30;   // Inner knob radius

  const updatePosition = (clientX: number, clientY: number) => {
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
    setDragging(true);
    updatePosition(event.clientX, event.clientY);
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    if (!dragging) return;

    updatePosition(event.clientX, event.clientY);
  };

  const handleMouseUp = () => {
    setDragging(false);

    // Return to center
    setPosition({ x: 0, y: 0 });
    onMove(0, 0);
  };

  const handleTouchStart = (event: React.TouchEvent) => {
    setDragging(true);

    const touch = event.touches[0];
    updatePosition(touch.clientX, touch.clientY);
  };

  const handleTouchMove = (event: React.TouchEvent) => {
    if (!dragging) return;

    const touch = event.touches[0];
    updatePosition(touch.clientX, touch.clientY);
  };

  const handleTouchEnd = () => {
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
        width: '100vw',
        height: '100vh',
      }}
    >
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