import React from "react";
import {
  Text,
} from "@radix-ui/themes";
import Wrapper from "@/wrapper";
import { axiosInstance } from "@/utils/session";
import { LogEntry as LogEntryType } from "@/utils";
import LogEntry from "./logEntry";

interface Params {
  id: string;
}

export default async function LogEntryDetail({ params }: { params: Params }) {
  const { id } = params;

  const res = await axiosInstance.get<LogEntryType>(`/api/logs/${id}/`);
  const logEntry = res.data;

  if (!logEntry) {
    return (
      <Wrapper>
        <Text size="4">Loading...</Text>
      </Wrapper>
    );
  }

  const logDate = new Date(logEntry.date).toLocaleDateString();

  return (
    <Wrapper>
      <LogEntry logDate={logDate} logEntry={logEntry} />
    </Wrapper>
  );
}
