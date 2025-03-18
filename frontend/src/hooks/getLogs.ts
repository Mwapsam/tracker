"use server";

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



export default async function fetchLogs(): Promise<LogEntry[]> {
  try {
    const res = await axiosInstance.get("/api/logs/");

    return res.data;
  } catch (error) {
    throw new Error(error as string);
  }
}
