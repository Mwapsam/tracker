"use client";

import React, { useState, ChangeEvent, FormEvent } from "react";
import { Box, Button, Flex } from "@radix-ui/themes";
import Wrapper from "@/wrapper";

interface VehicleFormData {
  truckNumber: string;
  trailerNumber: string;
  vin: string;
  carrier: string; 
}

export default function VehicleForm() {
  const [formData, setFormData] = useState<VehicleFormData>({
    truckNumber: "",
    trailerNumber: "",
    vin: "",
    carrier: "",
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log("Vehicle Submitted:", formData);
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
          Create Vehicle
        </h1>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
          <Flex direction={"column"}>
            <label htmlFor="truckNumber">Truck Number</label>
            <input
              type="text"
              id="truckNumber"
              name="truckNumber"
              placeholder="Enter truck number"
              value={formData.truckNumber}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            />
          </Flex>
          <Flex direction={"column"}>
            <label htmlFor="trailerNumber">Trailer Number</label>
            <input
              type="text"
              id="trailerNumber"
              name="trailerNumber"
              placeholder="Enter trailer number"
              value={formData.trailerNumber}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            />
          </Flex>
          <Flex direction={"column"}>
            <label htmlFor="vin">VIN</label>
            <input
              type="text"
              id="vin"
              name="vin"
              placeholder="Enter vehicle VIN"
              value={formData.vin}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            />
          </Flex>
          <Flex direction={"column"}>
            <label htmlFor="carrier">Carrier (ID or Name)</label>
            <input
              type="text"
              id="carrier"
              name="carrier"
              placeholder="Enter carrier identifier"
              value={formData.carrier}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            />
          </Flex>
          <Button
            type="submit"
            size={"4"}
            style={{ marginTop: "1rem" }}
            color="gray"
            variant="solid"
            highContrast
          >
            Submit Vehicle
          </Button>
        </form>
      </Box>
    </Wrapper>
  );
}
