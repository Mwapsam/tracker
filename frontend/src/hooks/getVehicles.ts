"use server";

import { Vehicle } from "@/utils";
import { axiosInstance } from "@/utils/session";
import axios from "axios";

export default async function fetchVehicles(): Promise<
  { data: Vehicle[] } | undefined
> {
  try {
    const res = await axiosInstance.get<Vehicle[]>("/api/vehicles/");
    return res;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.message);
    }
  }
}
