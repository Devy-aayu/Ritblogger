"use client";

import { useEffect, useState } from "react";
import { Loader2, Play, Pause, PlayCircle } from "lucide-react";

import { apiGet, apiPost } from "../../lib/api";

type Status = {
  enabled: boolean;
  paused: boolean;
  running: boolean;
  min_interval_hours: number;
  max_interval_hours: number;
  max_posts_per_day: number;
  status: string;
};

export default function AutomationControl() {
  const [status, setStatus] = useState<Status | null>(null);
  const [minHours, setMinHours] = useState(5);
  const [maxHours, setMaxHours] = useState(10);
  const [daily, setDaily] = useState(4);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function load() {
    try {
      const data = await apiGet<Status>("/api/automation/status");
      setStatus(data);
      setMinHours(data.min_interval_hours);
      setMaxHours(data.max_interval_hours);
      setDaily(data.max_posts_per_day);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load automation.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function save(enabled: boolean) {
    setLoading(true);
    setMessage("");

    try {
      await apiPost("/api/settings/automation", {
        enabled,
        min_interval_hours: minHours,
        max_interval_hours: maxHours,
        max_posts_per_day: daily,
      });
      await load();
      setMessage(enabled ? "Automation enabled." : "Automation paused.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not update automation.");
    } finally {
      setLoading(false);
    }
  }

  async function runNow() {
    setLoading(true);
    setMessage("");
    try {
      const result = await apiPost<{ success: boolean; message?: string; article?: { article?: { title?: string } } }>(
        "/api/automation/run",
      );
      setMessage(
        result.article?.article?.title
          ? `Published: ${result.article.article.title}`
          : result.message || "Run completed.",
      );
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Automation run failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="setup-card" style={{ marginTop: 16 }}>
      <div className="setup-heading">
        <div className="setup-icon">
          <PlayCircle size={22} />
        </div>
        <div>
          <h2>AI publishing automation</h2>
          <p>Trend scan → editorial research → SEO brief → article → duplicate check → GitHub publish.</p>
        </div>
      </div>

      <div className="form-grid">
        <label>
          <span>Minimum interval (hours)</span>
          <input type="number" min={1} max={168} value={minHours} onChange={(event) => setMinHours(Number(event.target.value))} />
        </label>

        <label>
          <span>Maximum interval (hours)</span>
          <input type="number" min={1} max={168} value={maxHours} onChange={(event) => setMaxHours(Number(event.target.value))} />
        </label>

        <label>
          <span>Maximum posts per day</span>
          <input type="number" min={1} max={20} value={daily} onChange={(event) => setDaily(Number(event.target.value))} />
        </label>

        <div>
          <span style={{ color: "var(--muted)", fontSize: 12 }}>
            Current state: {status?.status || "loading"}
          </span>
        </div>
      </div>

      <div style={{ display: "flex", gap: 10, marginTop: 20, flexWrap: "wrap" }}>
        <button className="connect-button" onClick={() => save(true)} disabled={loading}>
          {loading ? <Loader2 size={16} className="spin" /> : <Play size={16} />}
          Enable automation
        </button>

        <button className="secondary-button" onClick={() => save(false)} disabled={loading}>
          <Pause size={16} />
          Pause
        </button>

        <button className="secondary-button" onClick={runNow} disabled={loading || !!status?.running}>
          <PlayCircle size={16} />
          Run now
        </button>
      </div>

      {message && <div className="result success"><div>{message}</div></div>}
    </div>
  );
}
