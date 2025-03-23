"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";

interface MapWithRouteProps {
  waypoints: {
    lat: number;
    lng: number;
    locationName: string;
    status: string;
    start_time: string;
    end_time: string;
  }[];
}

export default function MapWithRoute({ waypoints }: MapWithRouteProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [currentPositionIndex, setCurrentPositionIndex] = useState(0);
  const markersRef = useRef<google.maps.Marker[]>([]);
  const polylineRef = useRef<google.maps.Polyline | null>(null);
  const animationRef = useRef<number | null>(null);
  const mapInstance = useRef<google.maps.Map | null>(null);
  const vehicleMarker = useRef<google.maps.Marker | null>(null);

  const statusColors = {
    D: "#FF0000",
    ON: "#FFA500",
    OFF: "#008000",
    SB: "#0000FF",
  };

  const calculateDistance = (
    start: google.maps.LatLng,
    end: google.maps.LatLng
  ) => {
    const R = 6371;
    const dLat = (end.lat() - start.lat()) * (Math.PI / 180);
    const dLon = (end.lng() - start.lng()) * (Math.PI / 180);
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(start.lat() * (Math.PI / 180)) *
        Math.cos(end.lat() * (Math.PI / 180)) *
        Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  };

  const calculateBearing = (
    start: google.maps.LatLng,
    end: google.maps.LatLng
  ) => {
    const y = Math.sin(end.lng() - start.lng()) * Math.cos(end.lat());
    const x =
      Math.cos(start.lat()) * Math.sin(end.lat()) -
      Math.sin(start.lat()) *
        Math.cos(end.lat()) *
        Math.cos(end.lng() - start.lng());
    return (Math.atan2(y, x) * 180) / Math.PI;
  };

  const animate = useCallback(() => {
    if (!vehicleMarker.current || currentPositionIndex >= waypoints.length - 1)
      return;

    const start = waypoints[currentPositionIndex];
    const end = waypoints[currentPositionIndex + 1];
    const startLatLng = new google.maps.LatLng(start.lat, start.lng);
    const endLatLng = new google.maps.LatLng(end.lat, end.lng);

    const distance = calculateDistance(startLatLng, endLatLng);
    const duration =
      (new Date(end.start_time).getTime() -
        new Date(start.end_time).getTime()) /
      1000;
    const speed = duration > 0 ? (distance / duration) * 3.6 : 0; 

    const step = 0.02 * (speed / 80);
    const currentProgress = { value: 0 };

    const animateSegment = () => {
      if (currentProgress.value >= 1) {
        setCurrentPositionIndex((prev) => prev + 1);
        return;
      }

      const newPosition = google.maps.geometry.spherical.interpolate(
        startLatLng,
        endLatLng,
        currentProgress.value
      );

      if (vehicleMarker.current && newPosition) {
        vehicleMarker.current.setPosition(newPosition);
        vehicleMarker.current.setIcon({
          ...((vehicleMarker.current.getIcon() as google.maps.Icon) || {}),
          rotation: calculateBearing(
            vehicleMarker.current.getPosition() as google.maps.LatLng,
            endLatLng
          ),
        });
      }

      currentProgress.value += step;
      animationRef.current = requestAnimationFrame(animateSegment);
    };

    animateSegment();
  }, [currentPositionIndex, waypoints]);

  useEffect(() => {
    if (mapRef.current && waypoints.length > 0) {
      mapInstance.current = new google.maps.Map(mapRef.current, {
        zoom: 10,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
      });

      const bounds = new google.maps.LatLngBounds();
      waypoints.forEach(({ lat, lng }) => bounds.extend({ lat, lng }));
      mapInstance.current.fitBounds(bounds);

      markersRef.current = waypoints.map((wp, index) => {
        const marker = new google.maps.Marker({
          position: { lat: wp.lat, lng: wp.lng },
          map: mapInstance.current,
          title: wp.locationName,
          label: {
            text: (index + 1).toString(),
            color: "#FFFFFF",
          },
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: statusColors[wp.status as keyof typeof statusColors],
            fillOpacity: 1,
            strokeColor: "#000000",
            strokeWeight: 2,
          },
        });

        const infoWindow = new google.maps.InfoWindow({
          content: `
            <div class="p-2">
              <h3 class="font-bold">${wp.locationName}</h3>
              <p>Status: ${wp.status}</p>
              <p>Time: ${new Date(
                wp.start_time
              ).toLocaleTimeString()} - ${new Date(
            wp.end_time
          ).toLocaleTimeString()}</p>
            </div>
          `,
        });

        marker.addListener("click", () =>
          infoWindow.open(mapInstance.current, marker)
        );
        return marker;
      });

      polylineRef.current = new google.maps.Polyline({
        path: waypoints.map((wp) => ({ lat: wp.lat, lng: wp.lng })),
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 0.7,
        strokeWeight: 3,
        map: mapInstance.current,
      });

      vehicleMarker.current = new google.maps.Marker({
        position: waypoints[0],
        map: mapInstance.current,
        icon: {
          path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          scale: 6,
          fillColor: "#34A853",
          fillOpacity: 1,
          strokeWeight: 2,
          rotation: 0,
        },
      });

      animate();

      return () => {
        if (animationRef.current) cancelAnimationFrame(animationRef.current);
        markersRef.current.forEach((marker) => marker.setMap(null));
        if (polylineRef.current) polylineRef.current.setMap(null);
        if (vehicleMarker.current) vehicleMarker.current.setMap(null);
        mapInstance.current = null;
      };
    }
  }, [waypoints, animate]);

  useEffect(() => {
    if (currentPositionIndex < waypoints.length - 1) {
      animationRef.current = requestAnimationFrame(() => animate());
    }
  }, [currentPositionIndex, waypoints, animate]);

  return (
    <div className="relative">
      <div
        ref={mapRef}
        style={{ width: "100%", height: "670px", borderRadius: "8px" }}
      />
    </div>
  );
}
