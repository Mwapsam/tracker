import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Theme } from "@radix-ui/themes";
import "./globals.css";
import Script from "next/script";

import "@radix-ui/themes/styles.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tracking App",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <Script
          src={`https://maps.googleapis.com/maps/api/js?key=${process.env.GOOGLE_MAPS_API_KEY}&libraries=geometry,places`}
          strategy="beforeInteractive"
          async={true}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Theme>{children}</Theme>
      </body>
    </html>
  );
}
