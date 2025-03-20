"use server";

import axios from "axios";
import { axiosInstance } from "@/utils/session";

interface DutyStatus {
  status: string;
  start_time: string;
  end_time: string;
  location: {
    lat: number;
    lon: number;
    name: string;
  };
}

interface LogEntry {
  id: number;
  date: string;
  vehicle: string;
  start_odometer: number;
  end_odometer: number;
  total_miles: number;
  remarks: string;
  signature: string;
  duty_statuses: DutyStatus[];
}

export default async function fetchLogs(retries = 3): Promise<LogEntry[]> {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const res = await axiosInstance.get<LogEntry[]>("/api/logs/");
      return res.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage =
          error.response?.data &&
          typeof error.response.data === "object" &&
          "message" in error.response.data
            ? error.response.data.message
            : error.message || "Failed to fetch logs";

        console.warn(`Attempt ${attempt} failed: ${errorMessage}`);

        if (attempt === retries) {
          console.error("Final attempt failed:", errorMessage);
          throw new Error(errorMessage);
        }
      } else if (error instanceof Error) {
        console.warn(`Attempt ${attempt} failed: ${error.message}`);

        if (attempt === retries) {
          console.error("Final attempt failed:", error.message);
          throw new Error(error.message);
        }
      } else {
        console.error("Unknown error occurred", error);
        throw new Error("An unknown error occurred while fetching logs.");
      }
    }
  }
  throw new Error("Unexpected error in fetchLogs");
}
