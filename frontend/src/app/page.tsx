"use client";

import React, { useState, useEffect } from "react";
import { Box, Table } from "@radix-ui/themes";
import fetchLogs from "@/hooks/getLogs";

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

interface DailyLog {
  date: string;
  driving: number;
  onDuty: number;
  offDuty: number;
  sleeperBerth: number;
}

export default function Home() {
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  const [dailyLogs, setDailyLogs] = useState<DailyLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetchLogs();
        const data = res;

        if (data) {
          setLogEntries(data);
          aggregateDailyLogs(data);
        }
      } catch (error) {
        console.error("Error loading logs:", error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  console.log(logEntries);

  function aggregateDailyLogs(entries: LogEntry[]) {
    const aggregation: { [date: string]: DailyLog } = {};
    entries.forEach((entry) => {
      const date = entry.date;
      if (!aggregation[date]) {
        aggregation[date] = {
          date,
          driving: 0,
          onDuty: 0,
          offDuty: 0,
          sleeperBerth: 0,
        };
      }
      entry.duty_statuses.forEach((ds) => {
        const duration =
          (new Date(ds.end_time).getTime() -
            new Date(ds.start_time).getTime()) /
          (3600 * 1000);
        switch (ds.status) {
          case "D":
            aggregation[date].driving += duration;
            break;
          case "ON":
            aggregation[date].onDuty += duration;
            break;
          case "OFF":
            aggregation[date].offDuty += duration;
            break;
          case "SB":
            aggregation[date].sleeperBerth += duration;
            break;
          default:
            break;
        }
      });
    });
    setDailyLogs(Object.values(aggregation));
  }

  return (
    <Box
      className="p-4 rounded-md"
      style={{ background: "var(--gray-a2)", borderRadius: "var(--radius-3)" }}
    >
      <nav style={{ marginBottom: "1rem" }}>
        <a href="#" style={{ marginRight: "1rem" }}>
          Home
        </a>
        <a href="#" style={{ marginRight: "1rem" }}>
          Trips
        </a>
        <a href="#">Daily Logs</a>
      </nav>

      <section style={{ display: "grid", gap: "1rem", padding: "1rem" }}>
        {/* Trip Details Table */}
        <Box>
          <h2 style={{ marginBottom: "0.5rem" }}>Trip Details</h2>
          {loading ? (
            <p>Loading...</p>
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
                    <Table.Row key={entry.id}>
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

        {/* Daily Logs Table */}
        <Box>
          <h2 style={{ marginBottom: "0.5rem" }}>Daily Logs</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <Table.Root variant="surface">
              <Table.Header>
                <Table.Row>
                  <Table.ColumnHeaderCell>Date</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Driving (hrs)</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    On Duty, Not Driving (hrs)
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Off Duty (hrs)
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Sleeper Berth (hrs)
                  </Table.ColumnHeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {dailyLogs.map((log) => (
                  <Table.Row key={log.date}>
                    <Table.RowHeaderCell>{log.date}</Table.RowHeaderCell>
                    <Table.Cell>{log.driving.toFixed(1)}</Table.Cell>
                    <Table.Cell>{log.onDuty.toFixed(1)}</Table.Cell>
                    <Table.Cell>{log.offDuty.toFixed(1)}</Table.Cell>
                    <Table.Cell>{log.sleeperBerth.toFixed(1)}</Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table.Root>
          )}
        </Box>
      </section>
    </Box>
  );
}
