"use server";

import { Trip } from "@/utils";
import { axiosInstance } from "@/utils/session";
import axios from "axios";

export default async function fetchTrip(): Promise<Trip[] | null> {
  try {
    const res = await axiosInstance.get<Trip[]>("/api/trips/");
    console.log("Trips fetched successfully:", res.data);

    return res.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("Error fetching trips:", error.message);
    }
    return null;
  }
}
