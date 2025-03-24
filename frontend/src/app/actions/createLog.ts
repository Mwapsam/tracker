"use server";

import { LogEntryFormData } from "@/utils";
import { axiosInstance } from "@/utils/session";
import axios from "axios";

const createLog = async (formData: LogEntryFormData) => {
  try {
    const response = await axiosInstance.post(`/api/logs/`, formData);
    const data = response.data;
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(
        "Log creation failed:",
        error.response?.data || error.message
      );
      throw new Error(error.response?.data?.detail || "Log creation failed");
    } else {
      console.error("Log creation failed:", error);
      throw new Error("Log creation failed");
    }
  }
};

export default createLog;
