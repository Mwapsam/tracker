import Wrapper from "@/wrapper";
import LogEntryForm from "./form";
import { Driver, Vehicle } from "@/utils";
import { axiosInstance } from "@/utils/session";

export default async function Page() {
  const res = await axiosInstance.get<Driver[]>("/api/drivers/");
  const drivers = res.data;

  const res1 = await axiosInstance.get<Vehicle[]>("/api/vehicles/");
  const vehicles = res1.data;

  return (
    <Wrapper>
      <LogEntryForm drivers={drivers} vehicles={vehicles} />
    </Wrapper>
  );
}
