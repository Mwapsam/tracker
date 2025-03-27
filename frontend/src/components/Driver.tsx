"use client";

import React, { useEffect, useRef, useState, useMemo } from "react";
import {
  Card,
  Flex,
  Grid,
  Progress,
  Table,
  Badge,
  Button,
  Text,
  Box,
  Heading,
  Dialog,
  ScrollArea,
} from "@radix-ui/themes";
import {
  ClockIcon,
  MarginIcon,
  GearIcon,
  DashboardIcon,
  RocketIcon,
  BellIcon,
  PlusIcon,
  DownloadIcon,
} from "@radix-ui/react-icons";
import "./driver.css";
import { Trip, Vehicle } from "@/utils";
import fetchTrip from "@/hooks/getTrips";
import { completeTrip, createTrip, startTrip, updateLocation } from "@/hooks";
import GooglePlacesAutocomplete from "react-google-places-autocomplete";

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

  // Automatically get current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setFormData((prev) => ({
            ...prev,
            current_location: `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`,
          }));
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

  // Handle form input changes for non-autocomplete fields
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "current_cycle_used" ? parseFloat(value) || 0 : value,
    }));
  };

  // Create new trip
  const handleCreateTrip = async () => {
    setIsCreatingTrip(true);
    try {
      const data = {
        vehicle: formData.vehicle,
        current_location: formData.current_location,
        pickup_location: formData.pickup_location,
        dropoff_location: formData.dropoff_location,
        current_cycle_used: formData.current_cycle_used,
        driver: trips && trips[0]?.driver,
      };

      console.log(data);

      const newTrip = await createTrip(data);
      setTrips((prev) => (prev ? [newTrip, ...prev] : [newTrip]));

      setShowTripForm(false);
    } catch (error) {
      console.error("Failed to create trip:", error);
    } finally {
      setIsCreatingTrip(false);
    }
  };

  // Start trip
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

  // Complete trip
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

  // Update location
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

  // Calculate trip progress
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

  // Format duration for display
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

  // Initialize and update map
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


  // Add a useEffect to track time elapsed:
  useEffect(() => {
    if (isTripActive) {
      const interval = setInterval(() => {
        setFormData((prev) => ({
          ...prev,
          current_cycle_used: prev.current_cycle_used + 0.1, // Update every 6 minutes
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
      <Flex justify="between" align="center" mb="5">
        <Flex align="center" gap="4">
          <DashboardIcon width={32} height={32} />
          <Heading size="7" weight="bold">
            Driver Dashboard
          </Heading>
        </Flex>

        <Flex gap="3" align="center">
          <Dialog.Root open={showTripForm} onOpenChange={setShowTripForm}>
            <Dialog.Trigger>
              <Button variant="soft" disabled={isTripActive}>
                <PlusIcon /> New Trip
              </Button>
            </Dialog.Trigger>

            <Dialog.Content style={{ maxWidth: 550 }}>
              <Dialog.Title>Create New Trip</Dialog.Title>
              <Dialog.Description mb="4">
                Enter trip details to begin tracking
              </Dialog.Description>

              <Flex direction="column" gap="5">
                <label>
                  <Text as="div" size="2" mb="1" weight="bold">
                    Current Location
                  </Text>
                  <input
                    name="current_location"
                    value={formData.current_location}
                    onChange={handleInputChange}
                    placeholder="Enter current location"
                    className="custom-input"
                    disabled
                  />
                </label>
                <label>
                  <Text as="div" size="2" mb="1" weight="bold">
                    Pickup Location
                  </Text>
                  <GooglePlacesAutocomplete
                    selectProps={{
                      value:
                        typeof formData.pickup_location === "string"
                          ? {
                              label: formData.pickup_location,
                              value: formData.pickup_location,
                            }
                          : formData.pickup_location,
                      onChange: (value) =>
                        setFormData((prev) => ({
                          ...prev,
                          pickup_location: value
                            ? typeof value === "string"
                              ? value
                              : value.label
                            : "",
                        })),
                    }}
                  />
                </label>
                <label>
                  <Text as="div" size="2" mb="1" weight="bold">
                    Dropoff Location
                  </Text>
                  <GooglePlacesAutocomplete
                    selectProps={{
                      value:
                        typeof formData.dropoff_location === "string"
                          ? {
                              label: formData.dropoff_location,
                              value: formData.dropoff_location,
                            }
                          : formData.dropoff_location,

                      onChange: (value) =>
                        setFormData((prev) => ({
                          ...prev,
                          dropoff_location: value
                            ? typeof value === "string"
                              ? value
                              : value.label
                            : "",
                        })),
                    }}
                  />
                </label>
                <label>
                  <Text as="div" size="2" mb="1" weight="bold">
                    Current Cycle Used (Hrs)
                  </Text>
                  <input
                    name="current_cycle_used"
                    value={formData.current_cycle_used}
                    onChange={handleInputChange}
                    placeholder="Enter hours used"
                    className="custom-input"
                    type="number"
                    disabled
                  />
                </label>
                <Box style={{ flex: "1 1 20px" }}>
                  <Text size="2" mb="1" weight="bold">
                    Vehicle
                  </Text>
                  <select
                    name="vehicle"
                    value={formData.vehicle}
                    onChange={handleInputChange}
                    style={{
                      width: "100%",
                      padding: "0.5rem",
                      fontSize: "1rem",
                    }}
                  >
                    <option value="">-- Select Vehicle --</option>
                    {vehicles.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.truck_number} - {v.trailer_number || "No Trailer"}
                      </option>
                    ))}
                  </select>
                </Box>
              </Flex>

              <Flex gap="3" mt="4" justify="end">
                <Dialog.Close>
                  <Button variant="soft" color="gray">
                    Cancel
                  </Button>
                </Dialog.Close>
                <Button onClick={handleCreateTrip} disabled={isCreatingTrip}>
                  <RocketIcon /> {isCreatingTrip ? "Creating..." : "Start Trip"}
                </Button>
              </Flex>
            </Dialog.Content>
          </Dialog.Root>

          <Badge
            color={isTripActive ? "green" : "gray"}
            radius="full"
            size="2"
            variant="soft"
          >
            <Flex gap="2" align="center">
              <Box
                style={{
                  width: "8px",
                  height: "8px",
                  background: `var(--${isTripActive ? "green" : "gray"}-9)`,
                  borderRadius: "50%",
                }}
              />
              {isTripActive ? "Active - 70h/8d" : "No Active Trip"}
            </Flex>
          </Badge>
        </Flex>
      </Flex>

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
            </>
          )}
        </Flex>
      )}

      <Grid columns={{ initial: "1", md: "3" }} gap="6">
        <Flex direction="column" gap="6" style={{ gridColumn: "span 2" }}>
          <Card>
            <Flex direction="column" gap="4">
              <Flex justify="between" align="center">
                <Heading size="5">Trip Progress</Heading>
                <Flex gap="2">
                  <Button
                    variant={activeTab === "current" ? "solid" : "soft"}
                    size="1"
                    onClick={() => setActiveTab("current")}
                  >
                    Current Trip
                  </Button>
                  <Button
                    variant={activeTab === "logs" ? "solid" : "soft"}
                    size="1"
                    onClick={() => setActiveTab("logs")}
                  >
                    Log History
                  </Button>
                </Flex>
              </Flex>

              {activeTab === "current" ? (
                <>
                  <Flex gap="4" align="center">
                    <MarginIcon width={24} height={24} />
                    <Flex direction="column" flexGrow="1">
                      <Text weight="bold" size="4">
                        {trip
                          ? `${trip.current_location} → ${trip.dropoff_location}`
                          : "No trip data available"}
                      </Text>
                      <Text size="2" color="gray">
                        Via {trip?.pickup_location || "N/A"}
                      </Text>
                    </Flex>
                  </Flex>

                  <Progress value={progress} size="2" />

                  <Grid columns="3" gap="4">
                    <StatBlock
                      label="Estimated Time"
                      value={
                        trip?.estimated_duration || "N/A"
                          ? formatDuration(trip?.estimated_duration || "")
                          : "N/A"
                      }
                    />
                    <StatBlock
                      label="Distance Covered"
                      value={`${Math.round(
                        trip ? (progress / 100) * trip.distance : 0
                      ).toLocaleString()} mi / ${
                        trip?.distance?.toLocaleString() || "N/A"
                      } mi`}
                    />
                    <StatBlock
                      label="Average Speed"
                      value={`${trip?.average_speed ?? "N/A"} mph`}
                    />
                  </Grid>
                </>
              ) : (
                <ScrollArea
                  type="always"
                  scrollbars="vertical"
                  style={{ height: 300 }}
                >
                  <Table.Root>
                    <Table.Header>
                      <Table.Row>
                        <Table.ColumnHeaderCell>Date</Table.ColumnHeaderCell>
                        <Table.ColumnHeaderCell>
                          Activity
                        </Table.ColumnHeaderCell>
                        <Table.ColumnHeaderCell>
                          Location
                        </Table.ColumnHeaderCell>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {trip?.stops?.map((stop, index) => (
                        <Table.Row key={index}>
                          <Table.Cell>
                            {new Date(stop.scheduled_time).toLocaleDateString()}
                          </Table.Cell>
                          <Table.Cell>
                            <Badge color="blue" variant="soft">
                              Stop
                            </Badge>
                          </Table.Cell>
                          <Table.Cell>{stop.location_name}</Table.Cell>
                        </Table.Row>
                      ))}
                    </Table.Body>
                  </Table.Root>
                </ScrollArea>
              )}
            </Flex>
          </Card>

          <Card>
            <Flex direction="column" gap="4">
              <Flex justify="between" align="center">
                <Heading size="5">Route Visualization</Heading>
                <Button variant="soft" size="1">
                  <DownloadIcon /> Export Route
                </Button>
              </Flex>
              <Box
                ref={mapRef}
                style={{
                  height: 700,
                  borderRadius: "var(--radius-3)",
                  overflow: "hidden",
                }}
              />
            </Flex>
          </Card>

          <Card>
            <Flex direction="column" gap="4">
              <Heading size="5">Recent Activity</Heading>
              <Table.Root variant="surface">
                <Table.Header>
                  <Table.Row>
                    <Table.ColumnHeaderCell>Time</Table.ColumnHeaderCell>
                    <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
                    <Table.ColumnHeaderCell>Location</Table.ColumnHeaderCell>
                    <Table.ColumnHeaderCell>Details</Table.ColumnHeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {trip?.stops.map((stop, index) => (
                    <Table.Row key={index}>
                      <Table.Cell>
                        {new Date(stop.scheduled_time).toLocaleTimeString()}
                      </Table.Cell>
                      <Table.Cell>
                        <Badge color="blue" variant="soft" radius="full">
                          Stop
                        </Badge>
                      </Table.Cell>
                      <Table.Cell>{stop.location_name}</Table.Cell>
                      <Table.Cell>
                        <Button variant="ghost" size="1">
                          View Details
                        </Button>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table.Root>
            </Flex>
          </Card>
        </Flex>

        <Flex direction="column" gap="6">
          <Card>
            <Flex direction="column" gap="4">
              <Heading size="5">Vehicle Status</Heading>
              <Grid columns="2" gap="4">
                <StatBlock
                  icon={<GearIcon />}
                  label="Next Service"
                  value="1,200 mi" // Static data, not provided by API
                />
                <StatBlock
                  icon="⛽"
                  label="Fuel Level"
                  value="78%" // Static data, not provided by API
                />
              </Grid>
              <Flex gap="2">
                <Button variant="soft" size="2" radius="full">
                  Service History
                </Button>
                <Button variant="soft" size="2" radius="full">
                  Maintenance Logs
                </Button>
              </Flex>
            </Flex>
          </Card>

          <Card>
            <Flex direction="column" gap="4">
              <Heading size="5">Compliance Status</Heading>
              <Flex direction="column" gap="3">
                <Progress
                  value={trip ? (trip.remaining_hours / 70) * 100 : 0}
                  color="green"
                  size="2"
                />
                <Grid columns="2" gap="2">
                  <StatBlock
                    label="Remaining Hours"
                    value={trip ? trip.remaining_hours.toString() : "N/A"}
                  />
                  <StatBlock label="Cycle Type" value="70h/8d" />
                </Grid>
              </Flex>
              <Flex gap="2">
                <Button variant="soft" size="2" radius="full">
                  <ClockIcon /> Start Break
                </Button>
                <Button variant="soft" size="2" radius="full" color="red">
                  Emergency Stop
                </Button>
              </Flex>
            </Flex>
          </Card>

          <Card>
            <Flex direction="column" gap="4">
              <Flex gap="2" align="center">
                <BellIcon />
                <Heading size="5">Alerts & Notifications</Heading>
              </Flex>
              <Flex direction="column" gap="3">
                <AlertItem
                  type="warning"
                  title="Upcoming Rest Break"
                  message="Required break in 45 minutes"
                />
                <AlertItem
                  type="info"
                  title="Fuel Stop Reminder"
                  message="Next fuel stop in 150 miles"
                />
              </Flex>
            </Flex>
          </Card>

          <Card>
            <Flex direction="column" gap="4">
              <Heading size="5">Quick Actions</Heading>
              <Grid columns="2" gap="3">
                <Button variant="surface" size="2">
                  Add Note
                </Button>
                <Button variant="surface" size="2">
                  Report Issue
                </Button>
                <Button variant="surface" size="2">
                  View Regulations
                </Button>
                <Button variant="surface" size="2">
                  Contact Dispatch
                </Button>
              </Grid>
            </Flex>
          </Card>
        </Flex>
      </Grid>
    </div>
  );
};

const StatBlock = ({
  icon,
  label,
  value,
}: {
  icon?: React.ReactNode;
  label: string;
  value: string;
}) => (
  <Flex gap="3" align="center">
    {icon && <Box style={{ fontSize: "20px" }}>{icon}</Box>}
    <Flex direction="column">
      <Text size="1" color="gray">
        {label}
      </Text>
      <Text weight="bold" size="4">
        {value}
      </Text>
    </Flex>
  </Flex>
);

const AlertItem = ({
  type,
  title,
  message,
}: {
  type: "info" | "warning" | "error";
  title: string;
  message: string;
}) => (
  <Flex
    gap="3"
    p="3"
    style={{
      background: `var(--${type}-2)`,
      borderRadius: "var(--radius-3)",
      border: `1px solid var(--${type}-6)`,
    }}
  >
    <Box style={{ color: `var(--${type}-9)` }}>
      {type === "warning" ? "⚠️" : type === "error" ? "❗" : "ℹ️"}
    </Box>
    <Flex direction="column">
      <Text
        weight="bold"
        size="2"
        color={
          type === "info"
            ? "blue"
            : type === "warning"
            ? "orange"
            : type === "error"
            ? "red"
            : undefined
        }
      >
        {title}
      </Text>
      <Text size="1" color="gray">
        {message}
      </Text>
    </Flex>
  </Flex>
);

export default Driver;
