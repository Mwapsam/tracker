import Wrapper from "@/wrapper";
import { axiosInstance } from "@/utils/session";
import LogEntries from "@/components/logEntries";

export default async function Home() {
  const res = await axiosInstance.get("/api/logs/");

  
  return (
    <Wrapper>
      <LogEntries logEntries={res.data} />
    </Wrapper>
  );
}
