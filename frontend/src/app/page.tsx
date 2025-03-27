import Wrapper from "@/wrapper";
import { axiosInstance } from "@/utils/session";
import LogEntries from "@/components/logEntries";
import { User, Vehicle } from "@/utils";
import Driver from "@/components/Driver";
import { redirect } from "next/navigation";
import { isAxiosError } from "axios";

export default async function Home() {
  let logEntries = [];
  let currentUser: User | null = null;

  try {
    const res = await axiosInstance.get("/api/logs/");
    logEntries = res.data;
  } catch (error) {
    console.error("Error fetching logs:", error);
  }

  try {
    const res1 = await axiosInstance.get<User>("/api/current-user/");
    currentUser = res1.data;
  } catch (error: unknown) {
    if (
      isAxiosError(error) &&
      (error.response?.status === 403 || error.response?.status === 401)
    ) {
      redirect("/login");
    }
  }

  const admin = currentUser?.is_staff;

  let vehicles = [] as Vehicle[];

  try {
    const res1 = await axiosInstance.get<Vehicle[]>("/api/vehicles/");
    vehicles = res1.data;
  } catch {}

  return (
    <Wrapper>
      {admin ? (
        <>
          {logEntries.length > 0 ? (
            <LogEntries logEntries={logEntries} />
          ) : (
            <p className="text-red-500" style={{ margin: "6rem auto" }}>
              No log entries available.
            </p>
          )}
        </>
      ) : (
        <Driver vehicles={vehicles} />
      )}
    </Wrapper>
  );
}
