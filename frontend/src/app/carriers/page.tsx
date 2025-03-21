"use client";

import React, { useState, ChangeEvent, FormEvent } from "react";
import { Box, Button, Flex } from "@radix-ui/themes";
import Wrapper from "@/wrapper";

interface CarrierFormData {
  name: string;
  mcNumber: string;
  mainOfficeAddress: string;
  homeTerminalAddress: string;
  hosCycleChoice: "60" | "70";
}

export default function CarrierForm() {
  const [formData, setFormData] = useState<CarrierFormData>({
    name: "",
    mcNumber: "",
    mainOfficeAddress: "",
    homeTerminalAddress: "",
    hosCycleChoice: "70",
  });

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    console.log("Carrier Submitted:", formData);
    // Perform API call to create carrier here
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
          Create Carrier
        </h1>
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
          <Flex direction={"column"}>
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              name="name"
              placeholder="Enter carrier name"
              value={formData.name}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            />
          </Flex>
          <Flex direction={"column"}>
            <label htmlFor="mcNumber">MC Number</label>
            <input
              type="text"
              id="mcNumber"
              name="mcNumber"
              placeholder="Enter MC number"
              value={formData.mcNumber}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            />
          </Flex>
          <Flex direction={"column"}>
            <label htmlFor="mainOfficeAddress">Main Office Address</label>
            <textarea
              id="mainOfficeAddress"
              name="mainOfficeAddress"
              placeholder="Enter main office address"
              value={formData.mainOfficeAddress}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem", minHeight: "60px" }}
            />
          </Flex>
          <Flex direction={"column"}>
            <label htmlFor="homeTerminalAddress">Home Terminal Address</label>
            <textarea
              id="homeTerminalAddress"
              name="homeTerminalAddress"
              placeholder="Enter home terminal address"
              value={formData.homeTerminalAddress}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem", minHeight: "60px" }}
            />
          </Flex>
          <Flex direction={"column"}>
            <label htmlFor="hosCycleChoice">HOS Cycle</label>
            <select
              id="hosCycleChoice"
              name="hosCycleChoice"
              value={formData.hosCycleChoice}
              onChange={handleChange}
              style={{ padding: "0.5rem", fontSize: "1rem" }}
            >
              <option value="60">60-hour/7-day</option>
              <option value="70">70-hour/8-day</option>
            </select>
          </Flex>
          <Button
            type="submit"
            size={"4"}
            style={{ marginTop: "1rem" }}
            color="gray"
            variant="solid"
            highContrast
          >
            Submit Carrier
          </Button>
        </form>
      </Box>
    </Wrapper>
  );
}
