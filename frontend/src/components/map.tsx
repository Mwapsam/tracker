"use client";

import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";

export default function Map() {
  
  return (
    <MapContainer
      center={[51.505, -0.09]}
      zoom={13}
      style={{ height: "300px", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={[51.505, -0.09]}>
        <Popup>Hello from React Leaflet!</Popup>
      </Marker>
    </MapContainer>
  );
}
