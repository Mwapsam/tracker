import { User } from "@/utils";
import { axiosInstance } from "@/utils/session";
import axios from "axios";

export default async function fetchUser(): Promise<{ data: User } | undefined> {
  try {
    const res = await axiosInstance.get<User>("/api/current-user/");
    return res;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.message);
    }
  }
}
