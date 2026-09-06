import type { Metadata } from "next";

import "./globals.css";

import DashboardShell from "../components/layout/DashboardShell";


export const metadata: Metadata = {
  title: "Ritnav Blog Engine",
  description:
    "Ritnav automated blog research and publishing engine",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <DashboardShell>
          {children}
        </DashboardShell>
      </body>
    </html>
  );
}