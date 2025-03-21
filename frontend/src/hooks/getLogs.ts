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

export default async function fetchLogs() {
  try {
    const res = await axiosInstance.get<LogEntry[]>("/api/logs/");
    return { data: res.data };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.message);
    }
  }
}
