"use client";

import React, { useState, ChangeEvent, FormEvent } from "react";
import { Box, Button, Flex } from "@radix-ui/themes";
import Wrapper from "@/wrapper";

interface DriverFormData {
  licenseNumber: string;
  carrier: string; 
}

export default function DriverForm() {
  const [formData, setFormData] = useState<DriverFormData>({
    licenseNumber: "",
    carrier: "",
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log("Driver Submitted:", formData);
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
          Create Driver Profile
        </h1>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
          <Flex direction={"column"}>
            <label htmlFor="licenseNumber">License Number</label>
            <input
              type="text"
              id="licenseNumber"
              name="licenseNumber"
              placeholder="Enter driver license number"
              value={formData.licenseNumber}
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
            Submit Driver
          </Button>
        </form>
      </Box>
    </Wrapper>
  );
}
