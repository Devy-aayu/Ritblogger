"use client";

import Link from "next/link";
import {
  Activity,
  BarChart3,
  BookOpen,
  Bot,
  Clock3,
  FileText,
  Flame,
  Github,
  LayoutDashboard,
  Play,
  Search,
  Settings,
  Zap,
} 
from "lucide-react";
import { useEffect, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type AutomationStatus = {
  enabled: boolean;
  status: string;
  message: string;
};

type SettingsData = {
  automation_enabled: boolean;
  min_interval_hours: number;
  max_interval_hours: number;
  max_posts_per_day: number;
  github_configured: boolean;
  ai_configured: boolean;
};

export default function DashboardPage() {
  const [status, setStatus] = useState<AutomationStatus | null>(null);
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState("");

  async function loadDashboard() {
    try {
      const [statusResponse, settingsResponse] = await Promise.all([
        fetch(`${API_URL}/api/automation/status`, {
          cache: "no-store",
        }),
        fetch(`${API_URL}/api/settings/`, {
          cache: "no-store",
        }),
      ]);

      if (statusResponse.ok) {
        setStatus(await statusResponse.json());
      }

      if (settingsResponse.ok) {
        setSettings(await settingsResponse.json());
      }
    } catch {
      setMessage("Backend is not reachable.");
    }
  }

  async function runNow() {
    setRunning(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/api/automation/run`, {
        method: "POST",
      });

      const data = await response.json();

      setMessage(data.message || "Automation request completed.");
      await loadDashboard();
    } catch {
      setMessage("Could not connect to the backend.");
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(loadDashboard, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Zap size={20} />
          </div>

          <div>
            <div className="brand-name">Ritnav</div>
            <div className="brand-subtitle">Blog Engine</div>
          </div>
        </div>

        <nav className="nav">
          <div className="nav-section">Workspace</div>

          <Link className="nav-item active" href="/">
            <LayoutDashboard size={18} />
            Dashboard
          </Link>

          <Link className="nav-item" href="/research">
            <Flame size={18} />
            Trending Topics
          </Link>

          <Link className="nav-item" href="/articles">
            <FileText size={18} />
            Articles
          </Link>

          <Link className="nav-item" href="/runs">
            <Activity size={18} />
            Automation Runs
          </Link>

          <div className="nav-section">System</div>

          <Link className="nav-item" href="/settings">
            <Settings size={18} />
            Settings
          </Link>
        </nav>

        <div className="sidebar-footer">
          <div className="connection-row">
            <span
              className={`status-dot ${
                settings?.github_configured ? "online" : ""
              }`}
            />
            GitHub
          </div>

          <div className="connection-row">
            <span
              className={`status-dot ${
                settings?.ai_configured ? "online" : ""
              }`}
            />
            AI Engine
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="page-label">Workspace</div>
            <h1>Dashboard</h1>
          </div>

          <div className="topbar-actions">
            <div className="system-status">
              <span
                className={`status-dot ${
                  status?.status === "running" ? "online" : ""
                }`}
              />
              {status?.status || "Loading"}
            </div>

            <button
              className="run-button"
              onClick={runNow}
              disabled={running}
            >
              <Play size={16} />
              {running ? "Running..." : "Run now"}
            </button>
          </div>
        </header>

        {message && <div className="notice">{message}</div>}

        <section className="stats-grid">
          <StatCard
            icon={<Bot size={20} />}
            label="Automation"
            value={settings?.automation_enabled ? "Enabled" : "Disabled"}
            detail={
              settings
                ? `${settings.min_interval_hours}-${settings.max_interval_hours} hr interval`
                : "Loading..."
            }
          />

          <StatCard
            icon={<BookOpen size={20} />}
            label="Published articles"
            value="0"
            detail="GitHub data will appear here"
          />

          <StatCard
            icon={<Flame size={20} />}
            label="Trend candidates"
            value="0"
            detail="Research engine pending"
          />

          <StatCard
            icon={<Clock3 size={20} />}
            label="Daily limit"
            value={settings ? String(settings.max_posts_per_day) : "—"}
            detail="Maximum articles per day"
          />
        </section>

        <section className="content-grid">
          <div className="panel large-panel">
            <div className="panel-header">
              <div>
                <div className="panel-kicker">Automation</div>
                <h2>Publishing engine</h2>
              </div>

              <span className="panel-badge">
                {status?.enabled ? "Active" : "Idle"}
              </span>
            </div>

            <div className="automation-card">
              <div className="automation-icon">
                <Bot size={28} />
              </div>

              <div className="automation-copy">
                <h3>Automated content pipeline</h3>

                <p>
                  Discover trending technology and science topics, research
                  them, generate SEO content, validate the result, and publish
                  it to the Ritnav repository.
                </p>

                <div className="pipeline">
                  <PipelineStep
                    icon={<Search size={15} />}
                    text="Research"
                  />
                  <PipelineStep
                    icon={<BarChart3 size={15} />}
                    text="SEO"
                  />
                  <PipelineStep
                    icon={<Bot size={15} />}
                    text="Generate"
                  />
                  <PipelineStep
                    icon={<Github size={15} />}
                    text="Publish"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <div className="panel-kicker">Repository</div>
                <h2>GitHub connection</h2>
              </div>
            </div>

            <div className="connection-card">
              <Github size={28} />

              <div>
                <strong>
                  {settings?.github_configured
                    ? "Connected"
                    : "Not configured"}
                </strong>

                <p>
                  {settings?.github_configured
                    ? "Ritnav repository is configured."
                    : "Add GitHub credentials in settings."}
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <div className="panel-kicker">Pipeline</div>
              <h2>Latest activity</h2>
            </div>
          </div>

          <div className="empty-state">
            <Activity size={32} />
            <h3>No automation runs yet</h3>
            <p>
              The research and publishing pipeline has not been connected
              yet.
            </p>

            <button
              className="secondary-button"
              onClick={runNow}
              disabled={running}
            >
              <Play size={15} />
              Start first run
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  detail,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>

      <div className="stat-label">{label}</div>

      <div className="stat-value">{value}</div>

      <div className="stat-detail">{detail}</div>
    </div>
  );
}

function PipelineStep({
  icon,
  text,
}: {
  icon: React.ReactNode;
  text: string;
}) {
  return (
    <div className="pipeline-step">
      {icon}
      <span>{text}</span>
    </div>
  );
}