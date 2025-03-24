import React from "react";
import { Box, Flex, Card, Text, Heading, Button } from "@radix-ui/themes";
import Wrapper from "@/wrapper";
import { axiosInstance } from "@/utils/session";
import MapWithRoute from "@/components/map";

type DutyStatus = {
  status: string;
  status_display: string;
  start_time: string;
  end_time: string;
  location: {
    lat: number | null;
    lon: number | null;
    name: string;
  };
};

export default async function DutyStatusDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const res = await axiosInstance.get<DutyStatus>(`/api/duty-status/${id}`);
  const dutyStatus = await res.data;

  if (!dutyStatus) {
    return (
      <Wrapper>
        <Text size="4">Loading...</Text>
      </Wrapper>
    );
  }

  const { status_display, start_time, end_time, location } = dutyStatus;
  const { lat, lon, name } = location;

  return (
    <Wrapper>
      <Box p="4" style={{ maxWidth: 1200, margin: "6rem auto" }}>
        <Flex align="center" justify="between" mb="4">
          <Heading size="6">Duty Status Detail</Heading>
          <Button variant="outline">Edit Duty Status</Button>
        </Flex>

        <Card variant="surface" mb="4">
          <Box p="4">
            <Text size="3" weight="bold" mb="1">
              {status_display}
            </Text>
            <div style={{ display: "flex", flexDirection: "column" }}>
              <Text size="2" color="gray">
                Start Time: {new Date(start_time).toLocaleString()}
              </Text>
              <Text size="2" color="gray">
                End Time: {new Date(end_time).toLocaleString()}
              </Text>
              <Text size="2" color="gray">
                Location: {name || "Unknown"}
              </Text>
            </div>
          </Box>
        </Card>

        <Card variant="surface">
          <Box p="4" style={{ width: "100%", height: "400px" }}>
            {lat && lon ? (
              <MapWithRoute
                waypoints={[
                  {
                    lat: 35.4655,
                    lng: -97.5217,
                    locationName: "Love's OKC",
                    status: "",
                    start_time: "",
                    end_time: "",
                  },
                  {
                    lat: 35.1875,
                    lng: -101.8346,
                    locationName: "Pilot Amarillo",
                    status: "",
                    start_time: "",
                    end_time: "",
                  },
                  {
                    lat: 35.0844,
                    lng: -106.6504,
                    locationName: "TA Albuquerque",
                    status: "",
                    start_time: "",
                    end_time: "",
                  },
                ]}
              />
            ) : (
              <Text size="2" color="gray">
                No valid coordinates available for map display.
              </Text>
            )}
          </Box>
        </Card>
      </Box>
    </Wrapper>
  );
}
