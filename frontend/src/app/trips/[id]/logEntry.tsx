"use client";

import MapWithRoute from "@/components/map";
import { LogEntry as LogEntryType } from "@/utils";
import {
  Avatar,
  Box,
  Button,
  Card,
  Flex,
  Grid,
  Heading,
  Separator,
  Text,
} from "@radix-ui/themes";
import React from "react";

type Props = {
  logDate: string;
  logEntry: LogEntryType;
};

const LogEntry = (props: Props) => {
  const { logDate, logEntry } = props;


  const mapData = logEntry.duty_statuses.map((data) => {
    return {
      lat: data.location.lat as number,
      lng: data.location.lon as number,
      locationName: data.location.name,
      status: data.status_display,
      start_time: data.start_time,
      end_time: data.end_time
    };
  });
  return (
    <Box p="4" style={{ maxWidth: 1200, margin: "6rem auto" }}>
      <Flex align="center" justify="between" mb="4">
        <Heading size="6">Log Entry Detail</Heading>
        <Button variant="outline">Edit Log Entry</Button>
      </Flex>

      <Card variant="surface" mb="4">
        <Flex align="center" justify="between">
          <Box width="500px">
            <Flex gap="4" align="center">
              <Avatar size="5" radius="full" fallback="T" color="indigo" />
              <Box>
                <Text as="div" size="4" weight="bold">
                  {logEntry.driver.user?.first_name}{" "}
                  {logEntry.driver.user?.last_name}
                </Text>
                <Text as="div" size="4" color="gray">
                  License: {logEntry.driver.license_number}
                </Text>
              </Box>
            </Flex>
          </Box>
          {logEntry.driver.carrier?.name && (
            <Text
              size="2"
              color="gray"
              style={{ display: "flex", flexDirection: "column" }}
            >
              <span style={{ color: "#000", fontWeight: "900" }}>Carrier:</span>{" "}
              <span>{logEntry.driver.carrier.name}</span>
            </Text>
          )}
        </Flex>
      </Card>

      {/* Quick Info Row */}
      <Grid columns={{ initial: "1", md: "4" }} gap="4">
        <Card size="3" style={{ display: "flex", flexDirection: "column" }}>
          <Text size="3" weight="bold">
            Date
          </Text>
          <Text size="2" color="gray">
            {logDate}
          </Text>
        </Card>

        <Card size="3" style={{ display: "flex", flexDirection: "column" }}>
          <Text size="3" weight="bold">
            Vehicle
          </Text>
          <Text size="2" color="gray">
            {logEntry.vehicle.truck_number} –{" "}
            {logEntry.vehicle.trailer_number || "No Trailer"}
          </Text>
        </Card>

        <Card size="3" style={{ display: "flex", flexDirection: "column" }}>
          <Text size="3" weight="bold">
            Odometer
          </Text>
          <Text size="2" color="gray">
            {logEntry.start_odometer} → {logEntry.end_odometer}
          </Text>
        </Card>

        <Card size="3" style={{ display: "flex", flexDirection: "column" }}>
          <Text size="3" weight="bold">
            Signature
          </Text>
          <Text size="2" color="gray">
            {logEntry.signature}
          </Text>
        </Card>
      </Grid>

      <Separator my="4" />

      {/* Remarks */}
      <Flex direction={{ initial: "column", md: "row" }} gap="4">
        <Card
          size="3"
          style={{ display: "flex", flexDirection: "column", flex: 1 }}
        >
          <Text size="3" weight="bold" mb="2">
            Remarks
          </Text>
          <Text size="2" color="gray">
            {logEntry.remarks || "No remarks"}
          </Text>
        </Card>
      </Flex>

      <Separator my="4" />

      <Card variant="surface">
        <Box p="4" style={{ width: "100%", height: "700px" }}>
          {mapData ? (
            <MapWithRoute waypoints={mapData} />
          ) : (
            <Text size="2" color="gray">
              No valid coordinates available for map display.
            </Text>
          )}
        </Box>
      </Card>

      <Separator my="4" />

      <Heading size="5" mb="2">
        Duty Statuses
      </Heading>
      {logEntry.duty_statuses?.length === 0 && (
        <Text size="2" color="gray">
          No duty statuses available.
        </Text>
      )}
      <Grid columns={{ initial: "1", md: "2" }} gap="4">
        {logEntry.duty_statuses?.map((status, idx) => {
          const startTime = new Date(status.start_time).toLocaleString();
          const endTime = new Date(status.end_time).toLocaleString();

          return (
            <Card
              key={idx}
              size="2"
            >
              <Flex direction="column" gap="1">
                <Text size="2" weight="bold">
                  {status.status_display}
                </Text>
                <Text size="2" color="gray">
                  {startTime} – {endTime}
                </Text>
                <Text size="2">
                  Location: {status.location.name} ({status.location.lat},{" "}
                  {status.location.lon})
                </Text>
              </Flex>
            </Card>
          );
        })}
      </Grid>
    </Box>
  );
};

export default LogEntry;
