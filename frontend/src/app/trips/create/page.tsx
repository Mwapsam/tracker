"use client";

import React, { useState, ChangeEvent, FormEvent } from "react";
import { Box, Flex, Card, Text, Heading, Button } from "@radix-ui/themes";
import Autocomplete from "react-google-autocomplete";
import Wrapper from "@/wrapper";

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
      <Box p="8" style={{ maxWidth: 1200, margin: "6rem auto" }}>
        <Card variant="surface" style={{ padding: "6" }}>
          <Heading size="6" mb="4" align="center">
            Record Driver&apos;s Log Entry
          </Heading>

          <form
            onSubmit={handleSubmit}
            style={{ display: "grid", gap: "1rem", margin: "1rem" }}
          >
            {/* Row 1: Date, Vehicle */}
            <Flex justify="between" wrap="wrap" gap="4">
              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Date
                </Text>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>

              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Vehicle (ID or number)
                </Text>
                <input
                  type="text"
                  name="vehicle"
                  placeholder="Enter vehicle identifier"
                  value={formData.vehicle}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>
            </Flex>

            {/* Row 2: Start Odometer, End Odometer */}
            <Flex justify="between" wrap="wrap" gap="4">
              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Start Odometer
                </Text>
                <input
                  type="number"
                  name="startOdometer"
                  placeholder="Enter start odometer"
                  value={formData.startOdometer}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>

              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  End Odometer
                </Text>
                <input
                  type="number"
                  name="endOdometer"
                  placeholder="Enter end odometer"
                  value={formData.endOdometer}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>
            </Flex>

            {/* Row 3: Signature */}
            <Box>
              <Text size="2" mb="1" weight="bold">
                Signature
              </Text>
              <input
                type="text"
                name="signature"
                placeholder="Driver's signature"
                value={formData.signature}
                onChange={handleChange}
                style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
              />
            </Box>

            {/* Row 4: Remarks */}
            <Box>
              <Text size="2" mb="1" weight="bold">
                Remarks
              </Text>
              <textarea
                name="remarks"
                placeholder="Enter remarks"
                value={formData.remarks}
                onChange={handleChange}
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  fontSize: "1rem",
                  minHeight: "80px",
                }}
              />
            </Box>

            {/* Row 5: Duty Window Start, Duty Window End */}
            <Flex justify="between" wrap="wrap" gap="4">
              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Duty Window Start
                </Text>
                <input
                  type="datetime-local"
                  name="dutyWindowStart"
                  value={formData.dutyWindowStart}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>

              <Box style={{ flex: "1 1 200px" }}>
                <Text size="2" mb="1" weight="bold">
                  Duty Window End
                </Text>
                <input
                  type="datetime-local"
                  name="dutyWindowEnd"
                  value={formData.dutyWindowEnd}
                  onChange={handleChange}
                  style={{ width: "100%", padding: "0.5rem", fontSize: "1rem" }}
                />
              </Box>
            </Flex>

            {/* Row 6: Adverse Conditions */}
            <Box>
              <label style={{ display: "flex", alignItems: "center" }}>
                <input
                  type="checkbox"
                  name="adverseConditions"
                  checked={formData.adverseConditions}
                  onChange={handleCheckboxChange}
                  style={{ marginRight: "0.5rem" }}
                />
                <Text size="2">Adverse Driving Conditions</Text>
              </label>
            </Box>

            {/* Duty Statuses */}
            <Box>
              <Text size="4" weight="bold" mb="2">
                Duty Statuses
              </Text>

              {formData.dutyStatuses.map((status, index) => (
                <Card
                  key={index}
                  variant="surface"
                  mb="3"
                  style={{ display: "grid", gap: "1rem" }}
                >
                  <Flex wrap="wrap" gap="2">
                    {/* Status */}
                    <Box style={{ flex: "1 1 150px" }}>
                      <Text size="2" mb="1" weight="bold">
                        Status
                      </Text>
                      <select
                        value={status.status}
                        onChange={(e) =>
                          handleDutyStatusChange(
                            index,
                            "status",
                            e.target.value
                          )
                        }
                        style={{
                          width: "100%",
                          padding: "0.5rem",
                          fontSize: "1rem",
                        }}
                      >
                        <option value="OFF">Off Duty</option>
                        <option value="SB">Sleeper Berth</option>
                        <option value="D">Driving</option>
                        <option value="ON">On Duty (Not Driving)</option>
                      </select>
                    </Box>

                    {/* Start Time */}
                    <Box style={{ flex: "1 1 150px" }}>
                      <Text size="2" mb="1" weight="bold">
                        Start Time
                      </Text>
                      <input
                        type="datetime-local"
                        value={status.startTime}
                        onChange={(e) =>
                          handleDutyStatusChange(
                            index,
                            "startTime",
                            e.target.value
                          )
                        }
                        style={{
                          width: "100%",
                          padding: "0.5rem",
                          fontSize: "1rem",
                        }}
                      />
                    </Box>

                    {/* End Time */}
                    <Box style={{ flex: "1 1 150px" }}>
                      <Text size="2" mb="1" weight="bold">
                        End Time
                      </Text>
                      <input
                        type="datetime-local"
                        value={status.endTime}
                        onChange={(e) =>
                          handleDutyStatusChange(
                            index,
                            "endTime",
                            e.target.value
                          )
                        }
                        style={{
                          width: "100%",
                          padding: "0.5rem",
                          fontSize: "1rem",
                        }}
                      />
                    </Box>

                    {/* Location (Autocomplete) */}
                    <Box style={{ flex: "1 1 300px" }}>
                      <Text size="2" mb="1" weight="bold">
                        Location
                      </Text>
                      <Autocomplete
                        apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}
                        onPlaceSelected={(place) => {
                          const formattedAddress =
                            place.formatted_address || "";
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
                          width: "100%",
                          padding: "0.5rem",
                          fontSize: "1rem",
                        }}
                      />
                    </Box>
                  </Flex>
                </Card>
              ))}

              <Button
                onClick={addDutyStatus}
                variant="soft"
                color="gray"
                size="2"
              >
                Add Duty Status
              </Button>
            </Box>

            {/* Submit Button */}
            <Button
              type="submit"
              size="4"
              color="gray"
              variant="solid"
              highContrast
              style={{ marginTop: "1rem" }}
            >
              Submit Log Entry
            </Button>
          </form>
        </Card>
      </Box>
    </Wrapper>
  );
}
