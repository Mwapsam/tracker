
import { Driver } from "@/utils";
import { axiosInstance } from "@/utils/session";
import axios from "axios";

export default async function fetchDrivers(): Promise<
  { data: Driver[] } | undefined
> {
  try {
    const res = await axiosInstance.get<Driver[]>("/api/drivers/");
    return res;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.message);
    }
  }
}
