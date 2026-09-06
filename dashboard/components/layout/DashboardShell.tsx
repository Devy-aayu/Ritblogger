"use client";

import Sidebar from "./Sidebar";

export default function DashboardShell({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        {children}
      </main>
    </div>
  );
}