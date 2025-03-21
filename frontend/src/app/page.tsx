"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Box, Table, Text } from "@radix-ui/themes";
import fetchLogs from "@/hooks/getLogs";
import Wrapper from "@/wrapper";

interface DutyStatus {
  status: string;
  start_time: string;
  end_time: string;
  location: {
    lat: number;
    lon: number;
    name: string;
  };
}

interface LogEntry {
  id: number;
  date: string;
  vehicle: string;
  start_odometer: number;
  end_odometer: number;
  total_miles: number;
  remarks: string;
  signature: string;
  duty_statuses: DutyStatus[];
}

export default function Home() {
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetchLogs();
        if (res) {
          setLogEntries(res.data);
        }
      } catch (error) {
        console.error("Error loading logs:", error);
        setError("Failed to load logs. Please try again later.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleRowClick = (id: number) => {
    router.push(`/trips/${id}`);
  };

  return (
    <Wrapper>
      <section
        style={{ display: "flex", padding: "1rem", justifyContent: "center" }}
      >
        <Box>
          <Text as="p" style={{ marginBottom: "0.5rem" }}>
            Trip Details
          </Text>
          {loading ? (
            <p>Loading trip details...</p>
          ) : error ? (
            <p style={{ color: "red" }}>{error}</p>
          ) : (
            <Table.Root variant="surface">
              <Table.Header>
                <Table.Row>
                  <Table.ColumnHeaderCell>Trip #</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Driver</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Current Location
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Pickup Location
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Dropoff Location
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Cycle Hrs Used
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Total Distance (miles)
                  </Table.ColumnHeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {logEntries.map((entry) => {
                  const firstStatus = entry.duty_statuses[0];
                  const lastStatus =
                    entry.duty_statuses[entry.duty_statuses.length - 1];
                  return (
                    <Table.Row
                      key={entry.id}
                      onClick={() => handleRowClick(entry.id)}
                      style={{ cursor: "pointer" }}
                    >
                      <Table.RowHeaderCell>{entry.id}</Table.RowHeaderCell>
                      <Table.Cell>{entry.signature}</Table.Cell>
                      <Table.Cell>
                        {lastStatus ? lastStatus.location.name : "N/A"}
                      </Table.Cell>
                      <Table.Cell>
                        {firstStatus ? firstStatus.location.name : "N/A"}
                      </Table.Cell>
                      <Table.Cell>
                        {lastStatus ? lastStatus.location.name : "N/A"}
                      </Table.Cell>
                      <Table.Cell>{"N/A"}</Table.Cell>
                      <Table.Cell>{entry.total_miles}</Table.Cell>
                    </Table.Row>
                  );
                })}
              </Table.Body>
            </Table.Root>
          )}
        </Box>
      </section>
    </Wrapper>
  );
}
