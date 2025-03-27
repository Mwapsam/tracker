import { Box } from "@radix-ui/themes";
import React from "react";



const Wrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <Box
      className="p-4 rounded-md"
      style={{
        background: "var(--gray-a2)",
        borderRadius: "var(--radius-3)",
        overflowY: "auto",
      }}
    >
      <nav
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          background: "#000",
          padding: "1rem",
          zIndex: 1000,
          boxShadow: "0px 2px 5px rgba(0,0,0,0.1)",
        }}
      >
        <a href="#" style={{ marginRight: "1rem" }}>
          Home
        </a>
        <a href="#" style={{ marginRight: "1rem" }}>
          Trips
        </a>
        <a href="#">Daily Logs</a>
      </nav>

      <Box>{children}</Box>
    </Box>
  );
};

export default Wrapper;
