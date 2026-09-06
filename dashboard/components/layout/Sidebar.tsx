"use client";

import Link from "next/link";
import {
  Activity,
  FileText,
  Flame,
  LayoutDashboard,
  Settings,
  Zap,
} from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <Zap size={20} />
        </div>

        <div>
          <div className="brand-name">
            Ritnav
          </div>

          <div className="brand-subtitle">
            Blog Engine
          </div>
        </div>
      </div>

      <nav className="nav">
        <div className="nav-section">
          Workspace
        </div>

        <Link
          className="nav-item"
          href="/"
        >
          <LayoutDashboard size={18} />
          Dashboard
        </Link>

        <Link
          className="nav-item"
          href="/research"
        >
          <Flame size={18} />
          Trending Topics
        </Link>

        <Link
          className="nav-item"
          href="/articles"
        >
          <FileText size={18} />
          Articles
        </Link>

        <Link
          className="nav-item"
          href="/runs"
        >
          <Activity size={18} />
          Automation Runs
        </Link>

        <div className="nav-section">
          System
        </div>

        <Link
          className="nav-item"
          href="/settings"
        >
          <Settings size={18} />
          Settings
        </Link>
      </nav>

      <div className="sidebar-footer">
        <div className="connection-row">
          <span className="status-dot online" />
          Backend
        </div>

        <div className="connection-row">
          <span className="status-dot online" />
          Automation
        </div>
      </div>
    </aside>
  );
}