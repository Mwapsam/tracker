"use client";

import React, { useState } from "react";
import {
  Box,
  Flex,
  Card,
  Text,
  Heading,
  Button,
  Table,
} from "@radix-ui/themes";
import Wrapper from "@/wrapper";
import { useRouter } from "next/navigation";
import { LogEntry } from "@/utils";

type Props = {
  logEntries: LogEntry[];
};

export default function LogEntries({ logEntries }: Props) {
  const router = useRouter();

  const [page, setPage] = useState(1);
  const pageSize = 15;

  const totalPages = Math.ceil(logEntries.length / pageSize);

  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const displayedEntries = logEntries.slice(startIndex, endIndex);

  const handleRowClick = (id: number) => {
    router.push(`/trips/${id}`);
  };

  const handleNext = () => {
    if (page < totalPages) {
      setPage((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (page > 1) {
      setPage((prev) => prev - 1);
    }
  };

  return (
    <Wrapper>
      <Box
        p="4"
        style={{ maxWidth: 1200, margin: "0 auto", marginTop: "6rem" }}
      >
        <Flex align="center" justify="between" mb="4">
          <Heading size="6">Trips Overview</Heading>
          <Button
            variant="outline"
            onClick={() => {
              router.push("/trips/create");
            }}
          >
            Add New Trip
          </Button>
        </Flex>

        <Card variant="surface">
          <Box p="4">
            <Text as="p" size="4" weight="bold" mb="2">
              Trip Details
            </Text>

            <Table.Root variant="ghost">
              <Table.Header>
                <Table.Row>
                  <Table.ColumnHeaderCell>Trip #</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Driver</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Start Odometer
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Vehicle (Truck Number)
                  </Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>End Odometer</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Total Miles</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Remarks</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>Signature</Table.ColumnHeaderCell>
                  <Table.ColumnHeaderCell>
                    Adverse Conditions
                  </Table.ColumnHeaderCell>
                </Table.Row>
              </Table.Header>

              <Table.Body>
                {displayedEntries.map((entry) => (
                  <Table.Row
                    key={entry.id}
                    onClick={() => handleRowClick(entry.id)}
                    style={{ cursor: "pointer" }}
                  >
                    <Table.RowHeaderCell>{entry.id}</Table.RowHeaderCell>
                    <Table.Cell>
                      {entry.driver.user.first_name}{" "}
                      {entry.driver.user.last_name}
                    </Table.Cell>
                    <Table.Cell>{entry.start_odometer}</Table.Cell>
                    <Table.Cell>{entry.vehicle.truck_number}</Table.Cell>
                    <Table.Cell>{entry.end_odometer}</Table.Cell>
                    <Table.Cell>{entry.total_miles}</Table.Cell>
                    <Table.Cell>{entry.remarks || "N/A"}</Table.Cell>
                    <Table.Cell>{entry.signature}</Table.Cell>
                    <Table.Cell>
                      {entry.adverse_conditions ? "Yes" : "No"}
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table.Root>

            <Flex align="center" justify="center" gap="2" mt="4">
              <Button
                onClick={handlePrevious}
                disabled={page <= 1}
                variant="soft"
              >
                Previous
              </Button>
              <Text size="2" as="span">
                Page {page} of {totalPages}
              </Text>
              <Button
                onClick={handleNext}
                disabled={page >= totalPages}
                variant="soft"
              >
                Next
              </Button>
            </Flex>
          </Box>
        </Card>
      </Box>
    </Wrapper>
  );
}
