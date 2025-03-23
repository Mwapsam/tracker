import { Box, Button, Card, Flex, Heading, Text } from "@radix-ui/themes";
import React from "react";

type Props = {
  status_display: string;
  start_time: string;
  end_time: string;
  location: {
    lat: number | null;
    lon: number | null;
    name: string;
  };
};

const DutyStatus = (props: Props) => {
  const { status_display, start_time, end_time, location } = props;
  const { lat, lon, name } = location;

  const googleMapsSrc = `https://www.google.com/maps/embed/v1/view?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&center=${lat},${lon}&zoom=14`;

  return (
    <Box p="4" style={{ maxWidth: 1200, margin: "auto" }}>
      {/* Header / Title */}
      <Flex align="center" justify="between" mb="4">
        <Heading size="6">Duty Status Detail</Heading>
        {/* Optional Action */}
        <Button variant="outline">Edit Duty Status</Button>
      </Flex>

      {/* Status Information */}
      <Card variant="surface" mb="4">
        <Box p="4">
          <Text size="3" weight="bold" mb="1">
            {status_display}
          </Text>
          <Text size="2" color="gray">
            Start Time: {new Date(start_time).toLocaleString()}
          </Text>
          <Text size="2" color="gray">
            End Time: {new Date(end_time).toLocaleString()}
          </Text>
          <Text size="2" color="gray">
            Location: {name || "Unknown"}
          </Text>
        </Box>
      </Card>

      {/* Map Embed */}
      <Card variant="surface">
        <Box p="4">
          {lat && lon ? (
            <Box style={{ width: "100%", height: "400px" }}>
              <iframe
                width="100%"
                height="100%"
                frameBorder="0"
                style={{ border: 0 }}
                src={googleMapsSrc}
                allowFullScreen
              />
            </Box>
          ) : (
            <Text size="2" color="gray">
              No valid coordinates available for map display.
            </Text>
          )}
        </Box>
      </Card>
    </Box>
  );
};

export default DutyStatus;
