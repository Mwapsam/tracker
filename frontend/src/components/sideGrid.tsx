import { Trip } from "@/utils";
import {
  BellIcon,
  ClockIcon,
  DownloadIcon,
  GearIcon,
  MarginIcon,
} from "@radix-ui/react-icons";
import {
  Badge,
  Box,
  Button,
  Card,
  Flex,
  Grid,
  Heading,
  Progress,
  ScrollArea,
  Table,
  Text,
} from "@radix-ui/themes";
import React from "react";

type Props = {
  activeTab: string;
  setActiveTab: React.Dispatch<React.SetStateAction<string>>;
  trip: Trip;
  progress: number;
  formatDuration: (duration: string) => string;
  mapRef: React.RefObject<HTMLDivElement | null>;
};

const SideGrid: React.FC<Props> = ({
  activeTab,
  setActiveTab,
  trip,
  progress,
  formatDuration,
  mapRef,
}) => {
  return (
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
                      <Table.ColumnHeaderCell>Activity</Table.ColumnHeaderCell>
                      <Table.ColumnHeaderCell>Location</Table.ColumnHeaderCell>
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

export default SideGrid;
