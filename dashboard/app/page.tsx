"use client";

import { useEffect, useState } from "react";

import {
  Activity,
  Bot,
  Clock3,
  Github,
  Play,
  Square,
} from "lucide-react";

import {
  apiGet,
  apiPost,
} from "../lib/api";


type AutomationStatus = {
  running: boolean;
  cycle_running: boolean;
  cycle_timeout_minutes: number;
  cycle_cooldown_minutes: number;
  last_started_at: string | null;
  last_finished_at: string | null;
  next_cycle_at: string | null;
  last_error: string | null;
  last_result: unknown;
};


export default function DashboardPage() {
  const [
    status,
    setStatus,
  ] = useState<AutomationStatus | null>(
    null,
  );


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    message,
    setMessage,
  ] = useState("");


  async function loadStatus() {
    try {
      const data =
        await apiGet<AutomationStatus>(
          "/api/automation/status",
        );

      setStatus(data);
    } catch {
      setMessage(
        "Backend is not reachable.",
      );
    }
  }


  async function runNow() {
    setLoading(true);
    setMessage(
      "Running one automation cycle...",
    );

    try {
      const data =
        await apiPost<any>(
          "/api/automation/run",
        );

      if (data.success) {
        setMessage(
          "Automation cycle completed.",
        );
      } else {
        setMessage(
          data.error ||
            "Automation cycle failed.",
        );
      }

      await loadStatus();
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Automation request failed.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function startAutomation() {
    setLoading(true);
    setMessage("");

    try {
      const data =
        await apiPost<any>(
          "/api/automation/start",
        );

      setMessage(
        data.message ||
          "Automation started.",
      );

      await loadStatus();
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Could not start automation.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function stopAutomation() {
    setLoading(true);
    setMessage("");

    try {
      const data =
        await apiPost<any>(
          "/api/automation/stop",
        );

      setMessage(
        data.message ||
          "Automation stopped.",
      );

      await loadStatus();
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Could not stop automation.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadStatus();

    const timer =
      setInterval(
        loadStatus,
        5000,
      );

    return () =>
      clearInterval(timer);
  }, []);


  return (
    <>
      <header className="topbar">
        <div>
          <div className="page-label">
            Workspace
          </div>

          <h1>
            Dashboard
          </h1>

          <p className="dashboard-description">
            Automated trend research, SEO,
            article generation and GitHub
            publishing.
          </p>
        </div>

        <div className="topbar-actions">
          <button
            className="run-button"
            onClick={runNow}
            disabled={
              loading ||
              status?.cycle_running
            }
          >
            <Play size={16} />

            {loading
              ? "Running..."
              : "Run one cycle"}
          </button>
        </div>
      </header>


      {message && (
        <div className="notice">
          {message}
        </div>
      )}


      <section className="stats-grid">
        <StatCard
          icon={<Bot size={19} />}
          label="Automation"
          value={
            status?.running
              ? "Running"
              : "Stopped"
          }
          detail="Automatic scheduler"
        />

        <StatCard
          icon={<Clock3 size={19} />}
          label="Cycle limit"
          value={
            `${status?.cycle_timeout_minutes ?? 5} min`
          }
          detail="Maximum execution time"
        />

        <StatCard
          icon={<Activity size={19} />}
          label="Cooldown"
          value={
            `${status?.cycle_cooldown_minutes ?? 10} min`
          }
          detail="Between completed cycles"
        />

        <StatCard
          icon={<Github size={19} />}
          label="Publisher"
          value="GitHub"
          detail="Ritnav repository"
        />
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <div className="panel-kicker">
              Automation
            </div>

            <h2>
              Content pipeline
            </h2>
          </div>

          {!status?.running ? (
            <button
              className="run-button"
              onClick={
                startAutomation
              }
              disabled={loading}
            >
              <Play size={15} />
              Start automation
            </button>
          ) : (
            <button
              className="secondary-button"
              onClick={
                stopAutomation
              }
              disabled={loading}
            >
              <Square size={14} />
              Stop automation
            </button>
          )}
        </div>


        <div className="automation-card">
          <div className="automation-icon">
            <Bot size={25} />
          </div>

          <div className="automation-copy">
            <h3>
              Automatic blog publishing
            </h3>

            <p>
              The engine researches live
              technology and science trends,
              analyzes the linked Ritnav
              blog.js structure, performs SEO
              research, generates an article,
              validates it and publishes it
              through GitHub.
            </p>
          </div>
        </div>
      </section>


      <section className="panel">
        <div className="panel-header">
          <div>
            <div className="panel-kicker">
              Latest cycle
            </div>

            <h2>
              Automation result
            </h2>
          </div>
        </div>


        {status?.cycle_running ? (
          <div className="empty-state">
            <Activity
              size={28}
              className="spin"
            />

            <h3>
              Cycle is running
            </h3>

            <p>
              Researching trends and
              processing the article pipeline.
            </p>
          </div>
        ) : status?.last_result ? (
          <pre className="result-console">
            {JSON.stringify(
              status.last_result,
              null,
              2,
            )}
          </pre>
        ) : (
          <div className="empty-state">
            <Activity size={28} />

            <h3>
              No cycle executed
            </h3>

            <p>
              Run one cycle to test the
              complete pipeline.
            </p>
          </div>
        )}
      </section>
    </>
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
      <div className="stat-icon">
        {icon}
      </div>

      <div className="stat-label">
        {label}
      </div>

      <div className="stat-value">
        {value}
      </div>

      <div className="stat-detail">
        {detail}
      </div>
    </div>
  );
}