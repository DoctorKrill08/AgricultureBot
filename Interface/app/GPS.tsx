'use client';
import './globals.css';
import 'leaflet/dist/leaflet.css';
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix default marker icon paths (Leaflet + bundlers issue)
const markerIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function parseGPSData(data: string) {
  const [latitude, longitude] = data.split(',');
  return [parseFloat(latitude),parseFloat(longitude)];
}

// Keeps the map centered as coordinates update live, without remounting the map
function Recenter({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng]);
  }, [lat, lng, map]);
  return null;
}

export default function GPS({ gpsData }: any) {
  const [measuredLatitude, measuredLongitude] = parseGPSData(gpsData);
  console.log(measuredLatitude, measuredLongitude)
  const [longitude, setLongitude] = useState(0);
  const [latitude, setLatitude] = useState(0);

  if (typeof measuredLongitude == 'number' && measuredLongitude != 0 && measuredLatitude != latitude && typeof measuredLatitude == 'number' && measuredLatitude != 0 && measuredLongitude != longitude && typeof measuredLongitude == 'number' && measuredLongitude != 0) {
    setLongitude(measuredLongitude);
    setLatitude(measuredLatitude);
  }

  return (
    <div>
      <h1 style={{ marginTop: 100 }}>
        GPS
      </h1>
      <p>
        Latitude: {latitude}
      </p>
      <p>
        Longitude: {longitude}
      </p>

      <div style={{ width: '300px', height: '300px', marginTop: 10 }}>
        <MapContainer
          center={[latitude, longitude]}
          zoom = {19}
          style={{ width: '100%', height: '100%' }}
        >
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={[latitude, longitude]} icon={markerIcon} />
          <Recenter lat={latitude} lng={longitude} />?
        </MapContainer>
      </div>
    </div>
  );
}
