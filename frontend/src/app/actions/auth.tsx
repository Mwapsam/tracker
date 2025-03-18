"use server";

import axios from "axios";
import { BASE_URL } from "@/utils";
import { storeToken } from "@/utils/session";

function normalizeUsername(username: string): string {
  const trimmed = username.trim();
  if (trimmed.includes("@")) {
    return trimmed.toLowerCase();
  }
  return trimmed.replace(/^0+/, "");
}

export async function login(formData: FormData) {
  const rawUsername = formData.get("username");
  const rawPassword = formData.get("password");

  if (typeof rawUsername !== "string" || typeof rawPassword !== "string") {
    throw new Error("Invalid form submission.");
  }

  const username = normalizeUsername(rawUsername);
  const password = rawPassword.trim();

  const payload = { username, password };

  try {
    const response = await axios.post(`${BASE_URL}/api/token/`, payload);
    const data = response.data;
    await storeToken(data.access, "access");
    await storeToken(data.refresh, "refresh");

    return data
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      console.error("Login failed:", error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || "Login failed");
    } else {
      console.error("Login failed:", error);
      throw new Error("Login failed");
    }
  }
}
