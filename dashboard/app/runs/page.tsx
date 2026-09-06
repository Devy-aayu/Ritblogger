"use client";

import { useEffect, useState } from "react";

type Run = {
  id?: string | number;
  status?: string;
  type?: string;
  topic?: string;
  title?: string;
  created_at?: string;
  started_at?: string;
  finished_at?: string;
  error?: string;
};

type RunsResponse = {
  runs?: Run[];
  count?: number;
};

export default function RunsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadRuns() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        "http://127.0.0.1:8000/api/runs/",
        {
          method: "GET",
          cache: "no-store",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to load runs (${response.status})`
        );
      }

      const data: RunsResponse = await response.json();

      setRuns(Array.isArray(data.runs) ? data.runs : []);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load runs."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRuns();

    const interval = setInterval(() => {
      loadRuns();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <main className="runs-page">
      <div className="page-header">
        <div>
          <h1>Runs</h1>
          <p>
            Monitor AI research, writing, validation, and publishing runs.
          </p>
        </div>

        <button
          type="button"
          onClick={loadRuns}
          className="refresh-button"
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error ? (
        <div className="runs-error">
          <strong>Unable to load runs</strong>
          <span>{error}</span>
        </div>
      ) : null}

      <section className="runs-card">
        <div className="runs-card-header">
          <h2>Recent runs</h2>
          <span>{runs.length}</span>
        </div>

        {loading && runs.length === 0 ? (
          <div className="runs-empty">
            Loading runs...
          </div>
        ) : runs.length === 0 ? (
          <div className="runs-empty">
            No runs have been recorded yet.
          </div>
        ) : (
          <div className="runs-list">
            {runs.map((run, index) => {
              const runKey =
                run.id ??
                `${run.created_at ?? "run"}-${index}`;

              const runName =
                run.title ||
                run.topic ||
                run.type ||
                "Automation run";

              const date =
                run.created_at ||
                run.started_at ||
                run.finished_at;

              return (
                <article
                  key={runKey}
                  className="run-row"
                >
                  <div className="run-main">
                    <h3>{runName}</h3>

                    {run.type ? (
                      <p>{run.type}</p>
                    ) : null}

                    {run.error ? (
                      <p className="run-error-text">
                        {run.error}
                      </p>
                    ) : null}
                  </div>

                  <div className="run-meta">
                    <span
                      className={`run-status ${
                        run.status
                          ? `status-${run.status.toLowerCase()}`
                          : ""
                      }`}
                    >
                      {run.status || "unknown"}
                    </span>

                    {date ? (
                      <time dateTime={date}>
                        {new Date(date).toLocaleString()}
                      </time>
                    ) : null}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <style jsx>{`
        .runs-page {
          padding: 32px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          margin-bottom: 24px;
        }

        .page-header h1 {
          margin: 0;
          font-size: 32px;
          line-height: 1.2;
        }

        .page-header p {
          margin: 8px 0 0;
          opacity: 0.7;
        }

        .refresh-button {
          border: 0;
          border-radius: 10px;
          padding: 10px 16px;
          cursor: pointer;
        }

        .refresh-button:disabled {
          opacity: 0.6;
          cursor: wait;
        }

        .runs-card {
          border-radius: 16px;
          overflow: hidden;
          border: 1px solid rgba(128, 128, 128, 0.2);
          background: rgba(255, 255, 255, 0.03);
        }

        .runs-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 18px 20px;
          border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        }

        .runs-card-header h2 {
          margin: 0;
          font-size: 18px;
        }

        .runs-card-header span {
          opacity: 0.7;
        }

        .runs-list {
          display: flex;
          flex-direction: column;
        }

        .run-row {
          display: flex;
          justify-content: space-between;
          gap: 20px;
          padding: 18px 20px;
          border-bottom: 1px solid rgba(128, 128, 128, 0.12);
        }

        .run-row:last-child {
          border-bottom: 0;
        }

        .run-main h3 {
          margin: 0;
          font-size: 16px;
        }

        .run-main p {
          margin: 6px 0 0;
          opacity: 0.65;
        }

        .run-error-text {
          opacity: 1 !important;
        }

        .run-meta {
          display: flex;
          align-items: flex-end;
          flex-direction: column;
          gap: 6px;
          white-space: nowrap;
        }

        .run-status {
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          font-weight: 600;
        }

        .run-meta time {
          font-size: 12px;
          opacity: 0.6;
        }

        .runs-empty {
          padding: 40px 20px;
          text-align: center;
          opacity: 0.65;
        }

        .runs-error {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin-bottom: 20px;
          padding: 16px;
          border-radius: 12px;
          border: 1px solid rgba(255, 90, 90, 0.3);
        }

        @media (max-width: 700px) {
          .runs-page {
            padding: 20px;
          }

          .page-header {
            align-items: flex-start;
            flex-direction: column;
          }

          .run-row {
            align-items: flex-start;
            flex-direction: column;
          }

          .run-meta {
            align-items: flex-start;
          }
        }
      `}</style>
    </main>
  );
}