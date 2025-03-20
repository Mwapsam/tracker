"use client";

import React, { useState } from "react";
import {
  Box,
  Button,
  Heading,
  Text,
  TextField,
  Spinner,
} from "@radix-ui/themes";
import { login } from "../actions/auth";

const Page = () => {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await login(new FormData(e.target as HTMLFormElement));

      if (res) {
        window.location.href = "/";
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

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

        {error && (
          <Text
            color="red"
            size={"2"}
            style={{ textAlign: "center" }}
          >
            {error}
          </Text>
        )}

        <Box as="div">
          <form
            onSubmit={handleSubmit}
            style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}
          >
            <TextField.Root
              type="text"
              name="username"
              placeholder="Username"
              value={formData.username}
              onChange={handleChange}
              required
            >
              <TextField.Slot />
            </TextField.Root>
            <TextField.Root
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
            >
              <TextField.Slot />
            </TextField.Root>
            <Button variant="solid" type="submit" disabled={loading}>
              {loading ? <Spinner size="1" /> : "Login"}
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
