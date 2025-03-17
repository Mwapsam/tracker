"use client";

import React from "react";
import { Box, Table } from "@radix-ui/themes";

export default function Home() {
  return (
    <Box
      style={{
        background: "var(--gray-a2)",
        borderRadius: "var(--radius-3)",
      }}
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
        {/* 1) Table for TRIP DETAILS */}
        <Box>
          <h2 style={{ marginBottom: "0.5rem" }}>Trip Details (Dummy Data)</h2>
          <Table.Root variant="surface">
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeaderCell>Trip #</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Driver</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>
                  Current Location
                </Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Pickup Location</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>
                  Dropoff Location
                </Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Cycle Hrs Used</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>
                  Total Distance (miles)
                </Table.ColumnHeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              <Table.Row>
                <Table.RowHeaderCell>1</Table.RowHeaderCell>
                <Table.Cell>Jane Driver</Table.Cell>
                <Table.Cell>Dallas, TX</Table.Cell>
                <Table.Cell>Fort Worth, TX</Table.Cell>
                <Table.Cell>Oklahoma City, OK</Table.Cell>
                <Table.Cell>24.0</Table.Cell>
                <Table.Cell>200</Table.Cell>
              </Table.Row>

              <Table.Row>
                <Table.RowHeaderCell>2</Table.RowHeaderCell>
                <Table.Cell>John Hauler</Table.Cell>
                <Table.Cell>Atlanta, GA</Table.Cell>
                <Table.Cell>Decatur, GA</Table.Cell>
                <Table.Cell>Nashville, TN</Table.Cell>
                <Table.Cell>48.5</Table.Cell>
                <Table.Cell>300</Table.Cell>
              </Table.Row>

              <Table.Row>
                <Table.RowHeaderCell>3</Table.RowHeaderCell>
                <Table.Cell>Maria Roadster</Table.Cell>
                <Table.Cell>Chicago, IL</Table.Cell>
                <Table.Cell>Joliet, IL</Table.Cell>
                <Table.Cell>St. Louis, MO</Table.Cell>
                <Table.Cell>63.0</Table.Cell>
                <Table.Cell>280</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table.Root>
        </Box>

        {/* 2) Table for DAILY LOGS */}
        <Box>
          <h2 style={{ marginBottom: "0.5rem" }}>Daily Logs (Dummy Data)</h2>
          <Table.Root variant="surface">
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeaderCell>Date</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Driving (hrs)</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>
                  On Duty, Not Driving (hrs)
                </Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>Off Duty (hrs)</Table.ColumnHeaderCell>
                <Table.ColumnHeaderCell>
                  Sleeper Berth (hrs)
                </Table.ColumnHeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              <Table.Row>
                <Table.RowHeaderCell>2023-10-01</Table.RowHeaderCell>
                <Table.Cell>8.5</Table.Cell>
                <Table.Cell>2.0</Table.Cell>
                <Table.Cell>13.5</Table.Cell>
                <Table.Cell>0</Table.Cell>
              </Table.Row>

              <Table.Row>
                <Table.RowHeaderCell>2023-10-02</Table.RowHeaderCell>
                <Table.Cell>9.0</Table.Cell>
                <Table.Cell>3.0</Table.Cell>
                <Table.Cell>12.0</Table.Cell>
                <Table.Cell>0</Table.Cell>
              </Table.Row>

              <Table.Row>
                <Table.RowHeaderCell>2023-10-03</Table.RowHeaderCell>
                <Table.Cell>7.5</Table.Cell>
                <Table.Cell>4.0</Table.Cell>
                <Table.Cell>10.5</Table.Cell>
                <Table.Cell>2.0</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table.Root>
        </Box>
      </section>
    </Box>
  );
}
