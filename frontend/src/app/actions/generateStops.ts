"use server";

import { axiosInstance } from "@/utils/session";
import axios from "axios";

const generateStops = async (tripId: string) => {
  try {
    const response = await axiosInstance.post(`/api/trips/${tripId}/stops/`);
    const data = response.data;
    return data;
  } catch (error) {
    console.log(error);
    
    if (axios.isAxiosError(error)) {
      console.error(
        "Stops generation failed:",
        error.response?.data || error.message
      );
      throw new Error(
        error.response?.data?.detail || "Stops generation failed"
      );
    } else {
      console.error("Stops generation failed:", error);
      throw new Error("Stops generation failed");
    }
  }
};

export default generateStops;
