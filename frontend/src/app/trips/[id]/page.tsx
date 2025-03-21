"use client";

import React, { useState, ChangeEvent, FormEvent } from "react";
import { Box, Button, Flex, Text } from "@radix-ui/themes";
import Autocomplete from "react-google-autocomplete";
import Wrapper from "../wrapper";

interface DutyStatusInput {
  status: string;
  startTime: string;
  endTime: string;
  locationName: string;
  locationLat: string;
  locationLon: string;
}

interface LogEntryFormData {
  date: string;
  vehicle: string;
  startOdometer: string;
  endOdometer: string;
  remarks: string;
  signature: string;
  adverseConditions: boolean;
  dutyWindowStart: string;
  dutyWindowEnd: string;
  dutyStatuses: DutyStatusInput[];
}

export default function LogEntryForm() {
  const [formData, setFormData] = useState<LogEntryFormData>({
    date: "",
    vehicle: "",
    startOdometer: "",
    endOdometer: "",
    remarks: "",
    signature: "",
    adverseConditions: false,
    dutyWindowStart: "",
    dutyWindowEnd: "",
    dutyStatuses: [],
  });

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, adverseConditions: e.target.checked });
  };

  const addDutyStatus = () => {
    setFormData({
      ...formData,
      dutyStatuses: [
        ...formData.dutyStatuses,
        {
          status: "OFF",
          startTime: "",
          endTime: "",
          locationName: "",
          locationLat: "",
          locationLon: "",
        },
      ],
    });
  };

  const handleDutyStatusChange = (
    index: number,
    field: string,
    value: string
  ) => {
    const updatedStatuses = formData.dutyStatuses.map((status, i) =>
      i === index ? { ...status, [field]: value } : status
    );
    setFormData({ ...formData, dutyStatuses: updatedStatuses });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log("Log Entry Submitted:", formData);
  };

  return (
    <Wrapper>
      <Box
        style={{
          padding: "2rem",
          backgroundColor: "#f9f9f9",
          borderRadius: "8px",
          maxWidth: "900px",
          margin: "0 auto",
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
        }}
      >
        <h1 style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          Record Driver&apos;s Log Entry
        </h1>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
          <Flex justify={"between"} wrap="wrap" gap="1rem">
            <Flex direction={"column"} style={{ flex: "1 1 200px" }}>
              <label htmlFor="date">Date</label>
              <input
                type="date"
                id="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                style={{ padding: "0.5rem", fontSize: "1rem" }}
              />
            </Flex>
            <Flex direction={"column"} style={{ flex: "1 1 200px" }}>
              <label htmlFor="vehicle">Vehicle (ID or number)</label>
              <input
                type="text"
                id="vehicle"
                name="vehicle"
                placeholder="Enter vehicle identifier"
                value={formData.vehicle}
                onChange={handleChange}
                style={{ padding: "0.5rem", fontSize: "1rem" }}
              />
            </Flex>
          </Flex>

          <Flex justify={"between"} wrap="wrap" gap="1rem">
            <Flex direction={"column"} style={{ flex: "1 1 200px" }}>
              <label htmlFor="startOdometer">Start Odometer</label>
              <input
                type="number"
                id="startOdometer"
                name="startOdometer"
                placeholder="Enter start odometer"
                value={formData.startOdometer}
                onChange={handleChange}
                style={{ padding: "0.5rem", fontSize: "1rem" }}
              />
            </Flex>
            <Flex direction={"column"} style={{ flex: "1 1 200px" }}>
              <label htmlFor="endOdometer">End Odometer</label>
              <input
                type="number"
                id="endOdometer"
                name="endOdometer"
                placeholder="Enter end odometer"
                value={formData.endOdometer}
                onChange={handleChange}
                style={{ padding: "0.5rem", fontSize: "1rem" }}
              />
            </Flex>
          </Flex>

          <Flex direction={"column"}>
            <label htmlFor="signature">Signature</label>
            <input
              type="text"
              id="signature"
              name="signature"
              placeholder="Driver's signature"
              value={formData.signature}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            />
          </Flex>

          <Flex direction={"column"}>
            <label htmlFor="remarks">Remarks</label>
            <textarea
              id="remarks"
              name="remarks"
              placeholder="Enter remarks"
              value={formData.remarks}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem", minHeight: "80px" }}
            />
          </Flex>

          <Flex justify={"between"} wrap="wrap" gap="1rem">
            <Flex direction={"column"} style={{ flex: "1 1 200px" }}>
              <label htmlFor="dutyWindowStart">Duty Window Start</label>
              <input
                type="datetime-local"
                id="dutyWindowStart"
                name="dutyWindowStart"
                value={formData.dutyWindowStart}
                onChange={handleChange}
                style={{ padding: "0.5rem", fontSize: "1rem" }}
              />
            </Flex>
            <Flex direction={"column"} style={{ flex: "1 1 200px" }}>
              <label htmlFor="dutyWindowEnd">Duty Window End</label>
              <input
                type="datetime-local"
                id="dutyWindowEnd"
                name="dutyWindowEnd"
                value={formData.dutyWindowEnd}
                onChange={handleChange}
                style={{ padding: "0.5rem", fontSize: "1rem" }}
              />
            </Flex>
          </Flex>

          <Flex direction={"column"}>
            <label
              htmlFor="adverseConditions"
              style={{ display: "flex", alignItems: "center" }}
            >
              <input
                type="checkbox"
                id="adverseConditions"
                name="adverseConditions"
                checked={formData.adverseConditions}
                onChange={handleCheckboxChange}
                style={{ marginRight: "0.5rem" }}
              />
              Adverse Driving Conditions
            </label>
          </Flex>

          <Box>
            <Text as="div" style={{ marginBottom: "1rem" }}>
              Duty Statuses
            </Text>
            {formData.dutyStatuses.map((status, index) => (
              <Flex
                key={index}
                wrap="wrap"
                gap="1rem"
                style={{
                  border: "1px solid #ddd",
                  padding: "1rem",
                  borderRadius: "4px",
                  marginBottom: "1rem",
                }}
              >
                <Flex direction={"column"} style={{ flex: "1 1 150px" }}>
                  <label>Status</label>
                  <select
                    value={status.status}
                    onChange={(e) =>
                      handleDutyStatusChange(index, "status", e.target.value)
                    }
                    style={{ padding: "0.5rem", fontSize: "1rem" }}
                  >
                    <option value="OFF">Off Duty</option>
                    <option value="SB">Sleeper Berth</option>
                    <option value="D">Driving</option>
                    <option value="ON">On Duty (Not Driving)</option>
                  </select>
                </Flex>
                <Flex direction={"column"} style={{ flex: "1 1 150px" }}>
                  <label>Start Time</label>
                  <input
                    type="datetime-local"
                    value={status.startTime}
                    onChange={(e) =>
                      handleDutyStatusChange(index, "startTime", e.target.value)
                    }
                    style={{ padding: "0.5rem", fontSize: "1rem" }}
                  />
                </Flex>
                <Flex direction={"column"} style={{ flex: "1 1 150px" }}>
                  <label>End Time</label>
                  <input
                    type="datetime-local"
                    value={status.endTime}
                    onChange={(e) =>
                      handleDutyStatusChange(index, "endTime", e.target.value)
                    }
                    style={{ padding: "0.5rem", fontSize: "1rem" }}
                  />
                </Flex>
                <Flex direction={"column"} style={{ flex: "1 1 300px" }}>
                  <label>Location</label>
                  <Autocomplete
                    apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}
                    onPlaceSelected={(place) => {
                      const formattedAddress = place.formatted_address || "";
                      const lat = place.geometry?.location?.lat();
                      const lon = place.geometry?.location?.lng();
                      handleDutyStatusChange(
                        index,
                        "locationName",
                        formattedAddress
                      );
                      handleDutyStatusChange(
                        index,
                        "locationLat",
                        lat ? lat.toString() : ""
                      );
                      handleDutyStatusChange(
                        index,
                        "locationLon",
                        lon ? lon.toString() : ""
                      );
                    }}
                    options={{ types: ["address"] }}
                    defaultValue={status.locationName}
                    style={{
                      padding: "0.5rem",
                      fontSize: "1rem",
                      width: "100%",
                    }}
                  />
                </Flex>
              </Flex>
            ))}
            <Button color="gray" size={"2"} onClick={addDutyStatus}>
              Add Duty Status
            </Button>
          </Box>

          <Button
            type="submit"
            size={"4"}
            style={{ marginTop: "1rem" }}
            color="gray"
            variant="solid"
            highContrast
          >
            Submit Log Entry
          </Button>
        </form>
      </Box>
    </Wrapper>
  );
}
