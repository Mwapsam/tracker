"use client";

import React, { useEffect, useRef, useState, useMemo } from "react";
import { Flex, Button, Text } from "@radix-ui/themes";
import "./driver.css";
import { Trip, Vehicle } from "@/utils";
import fetchTrip from "@/hooks/getTrips";
import { completeTrip, createTrip, startTrip, updateLocation } from "@/hooks";
import SideGrid from "./sideGrid";
import TopBox from "./topBox";
import generateStops from "@/app/actions/generateStops";

interface Props {
  vehicles: Vehicle[];
}

const Driver: React.FC<Props> = ({ vehicles }) => {
  const mapRef = useRef<HTMLDivElement>(null);

  const [activeTab, setActiveTab] = useState("current");
  const [showTripForm, setShowTripForm] = useState(false);
  const [trips, setTrips] = useState<Trip[] | null>(null);
  const [formData, setFormData] = useState<{
    current_location: string;
    pickup_location: string;
    dropoff_location: string;
    current_cycle_used: number;
    vehicle: string;
    driver: string;
  }>({
    current_location: "",
    pickup_location: "",
    dropoff_location: "",
    current_cycle_used: 0,
    vehicle: "",
    driver: "",
  });
  const [isCreatingTrip, setIsCreatingTrip] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchTrip();
        if (data) {
          setTrips(data);
        }
      } catch (error) {
        console.error("Failed to fetch trips:", error);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            const response = await fetch(
              `https://maps.googleapis.com/maps/api/geocode/json?latlng=${latitude},${longitude}&key=AIzaSyC9ik3lucRMBrV4-uliLe2717QYUGKmIDU`
            );
            const data = await response.json();

            if (data.status === "OK" && data.results.length > 0) {
              const locationName = data.results[0].formatted_address;
              setFormData((prev) => ({
                ...prev,
                current_location: locationName,
              }));
            } else {
              setFormData((prev) => ({
                ...prev,
                current_location: "Location not found",
              }));
            }
          } catch (error) {
            console.error("Reverse geocoding error:", error);
            setFormData((prev) => ({
              ...prev,
              current_location: "Location unavailable",
            }));
          }
        },
        (error) => {
          console.error("Geolocation error:", error);
          setFormData((prev) => ({
            ...prev,
            current_location: "Location unavailable",
          }));
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0,
        }
      );
    }
  }, []);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "current_cycle_used" ? parseFloat(value) || 0 : value,
    }));
  };

  const handleCreateTrip = async () => {
    setIsCreatingTrip(true);
    try {
      const data = {
        vehicle: formData.vehicle,
        current_location: formData.current_location,
        pickup_location: formData.pickup_location,
        dropoff_location: formData.dropoff_location,
        current_cycle_used: formData.current_cycle_used,
        driver: trips && (trips[0]?.driver as string),
      };

      const newTrip = await createTrip(data);
      setTrips((prev) => (prev ? [newTrip, ...prev] : [newTrip]));

      setShowTripForm(false);
    } catch (error) {
      console.error("Failed to create trip:", error);
    } finally {
      setIsCreatingTrip(false);
    }
  };

  const handleCreateStops = async () => {
    try {
      if (!trips || trips.length === 0) {
        console.error("No trips available to generate stops.");
        return;
      }
      const tripId = trips[0].id;
      const res = await generateStops(tripId);
      console.log(res);
    } catch (error) {
      console.error("Failed to generate stops! :", error);
    } finally {
      console.log("Failed!");
    }
  };

  const handleStartTrip = async (tripId: number) => {
    try {
      const updatedTrip = await startTrip(tripId);
      setTrips((prev) =>
        prev
          ? prev
              .map((trip) =>
                trip.id === tripId.toString() ? updatedTrip : trip
              )
              .filter((trip): trip is Trip => trip !== undefined)
          : null
      );
    } catch (error) {
      console.error("Failed to start trip:", error);
      alert(error instanceof Error ? error.message : "Failed to start trip");
    }
  };

  const handleCompleteTrip = async (tripId: number) => {
    try {
      const completedTrip = await completeTrip(tripId);
      setTrips(
        (prev) =>
          prev?.map((trip) =>
            Number(trip.id) === tripId ? completedTrip : trip
          ) || null
      );
    } catch (error) {
      console.error("Failed to complete trip:", error);
      alert(error instanceof Error ? error.message : "Failed to complete trip");
    }
  };

  const handleUpdateLocation = async (tripId: number, location: string) => {
    try {
      const updatedTrip = await updateLocation(tripId, location);
      setTrips(
        (prev) =>
          prev?.map((trip) =>
            Number(trip.id) === tripId ? updatedTrip : trip
          ) || null
      );
    } catch (error) {
      console.error("Failed to update location:", error);
    }
  };

  const progress = useMemo(() => {
    if (!trips?.[0]?.stops?.length || !trips[0].distance) return 0;
    return (
      (trips[0].stops.reduce((acc, stop) => {
        return (
          acc +
          (stop.actual_time && new Date(stop.actual_time) < new Date() ? 1 : 0)
        );
      }, 0) /
        trips[0].stops.length) *
      100
    );
  }, [trips]);

  const formatDuration = (duration: string) => {
    try {
      const [days, time] = duration.split(" ");
      const [hours, minutes] = time.split(":");
      return `${parseInt(days) * 24 + parseInt(hours)}h ${minutes}m remaining`;
    } catch {
      console.error("Invalid duration format:", duration);
      return "N/A";
    }
  };

  useEffect(() => {
    let map: google.maps.Map | null = null;
    let markers: google.maps.Marker[] = [];
    let route: google.maps.Polyline | null = null;

    const initMap = async () => {
      if (!window.google?.maps || !mapRef.current) return;

      try {
        const trip = trips?.[0];
        const stops = trip?.stops || [];
        const defaultCenter = { lat: 37.0902, lng: -95.7129 };

        const center =
          stops.length > 0
            ? { lat: stops[0].location_lat, lng: stops[0].location_lon }
            : defaultCenter;

        map = new window.google.maps.Map(mapRef.current, {
          center,
          zoom: stops.length > 0 ? 8 : 4,
          disableDefaultUI: true,
          gestureHandling: "cooperative",
        });

        if (stops.length) {
          markers = stops.map(
            (stop) =>
              new window.google.maps.Marker({
                position: { lat: stop.location_lat, lng: stop.location_lon },
                map,
                title: stop.location_name,
                icon: {
                  path: window.google.maps.SymbolPath.CIRCLE,
                  fillColor: "#4285F4",
                  fillOpacity: 1,
                  strokeColor: "white",
                  strokeWeight: 2,
                  scale: 8,
                },
              })
          );

          route = new window.google.maps.Polyline({
            path: stops.map((stop) => ({
              lat: stop.location_lat,
              lng: stop.location_lon,
            })),
            geodesic: true,
            strokeColor: "#4285F4",
            strokeOpacity: 0.7,
            strokeWeight: 4,
          });
          route.setMap(map);

          const bounds = new window.google.maps.LatLngBounds();
          stops.forEach((stop) =>
            bounds.extend(
              new window.google.maps.LatLng(
                stop.location_lat,
                stop.location_lon
              )
            )
          );
          map.fitBounds(bounds);
        }
      } catch (error) {
        console.error("Map initialization error:", error);
      }
    };

    initMap();

    return () => {
      markers.forEach((m) => m.setMap(null));
      route?.setMap(null);
    };
  }, [trips]);

  const trip = trips ? trips[0] : null;
  const isTripActive = trip ? !!trip.start_time && !trip.completed : false;

  console.log(formData);

  useEffect(() => {
    if (isTripActive) {
      const interval = setInterval(() => {
        setFormData((prev) => ({
          ...prev,
          current_cycle_used: prev.current_cycle_used + 0.1,
        }));
      }, 60000);
      return () => clearInterval(interval);
    }
  }, [isTripActive]);

  if (!trips) {
    return (
      <Flex justify="center" align="center" style={{ height: "100vh" }}>
        <Text>Loading...</Text>
      </Flex>
    );
  }

  return (
    <div className="driver-dashboard">
      <TopBox
        showTripForm={showTripForm}
        setShowTripForm={setShowTripForm}
        isTripActive={isTripActive}
        formData={formData}
        handleInputChange={handleInputChange}
        setFormData={setFormData}
        handleCreateTrip={handleCreateTrip}
        isCreatingTrip={isCreatingTrip}
        vehicles={vehicles}
      />

      {trip && (
        <Flex gap="3" mb="5">
          {!trip.start_time && (
            <Button onClick={() => handleStartTrip(Number(trip.id))}>
              Start Trip
            </Button>
          )}
          {isTripActive && (
            <>
              <Button onClick={() => handleCompleteTrip(Number(trip.id))}>
                Complete Trip
              </Button>
              <Button
                variant="soft"
                onClick={() => {
                  const newLocation = prompt("Enter new location:");
                  if (newLocation) {
                    handleUpdateLocation(Number(trip.id), newLocation);
                  }
                }}
              >
                Update Location
              </Button>

              <Button onClick={() => handleCreateStops()}>
                Generate Stops
              </Button>
            </>
          )}
        </Flex>
      )}

      <SideGrid
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        trip={trip as Trip}
        progress={progress}
        formatDuration={formatDuration}
        mapRef={mapRef}
      />
    </div>
  );
};

export default Driver;
