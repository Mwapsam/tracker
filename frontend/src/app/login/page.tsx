"use client";

import React from "react";
import { Box, Button, Heading, TextField } from "@radix-ui/themes";
import axios from "axios";

const Page = () => {
  async function createInvoice(formData: FormData) {
    const rawFormData = {
      username: formData.get("username"),
      password: formData.get("password"),
    };

    const response = await axios.post(
      "http://localhost:8000/api/token/",
      rawFormData
    );

    const data = await response.data;
    console.log(data);

    if (!response) {
      throw new Error(data.detail || "Login failed");
    }
  }
  return (
    <Box
      style={{
        minHeight: "100vh",
        background: "#f3f4f6",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Box
        style={{
          padding: "2rem",
          background: "#fff",
          borderRadius: "8px",
          boxShadow: "0px 4px 6px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: "400px",
        }}
      >
        <Heading
          as="h1"
          size="3"
          style={{ textAlign: "center", marginBottom: "1rem" }}
        >
          Welcome
        </Heading>
        <Box as="div">
          <form
            action={createInvoice}
            style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
          >
            <TextField.Root placeholder="Username" name="username">
              <TextField.Slot></TextField.Slot>
            </TextField.Root>

            <TextField.Root placeholder="Password" name="password">
              <TextField.Slot></TextField.Slot>
            </TextField.Root>

            <Button variant="solid" type="submit">
              Login
            </Button>
          </form>
        </Box>
        <Box
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: "1rem",
          }}
        >
          <Button variant="ghost" size="1">
            Forgot Password
          </Button>
          <Button variant="ghost" size="1">
            Help
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default Page;
