"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Cpu,
  Loader2,
  XCircle,
} from "lucide-react";

import { apiPost } from "../../lib/api";


type AIResult = {
  success: boolean;
  message: string;
  ai: {
    configured: boolean;
    provider: string;
    base_url: string;
    model: string;
  };
};


export default function AISetup() {
  const [provider, setProvider] =
    useState("");

  const [apiKey, setApiKey] =
    useState("");

  const [baseUrl, setBaseUrl] =
    useState("");

  const [model, setModel] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [result, setResult] =
    useState<AIResult | null>(null);

  const [error, setError] =
    useState("");


  async function saveAI() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data =
        await apiPost<AIResult>(
          "/api/settings/ai",
          {
            provider: provider.trim(),
            api_key: apiKey.trim(),
            base_url: baseUrl.trim(),
            model: model.trim(),
          },
        );

      setResult(data);

      setApiKey("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not configure AI provider.",
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="setup-card">
      <div className="setup-heading">
        <div className="setup-icon">
          <Cpu size={22} />
        </div>

        <div>
          <h2>Connect AI Provider</h2>

          <p>
            Use any OpenAI-compatible AI provider
            for topic analysis, SEO research and
            article generation.
          </p>
        </div>
      </div>


      <div className="setup-warning">
        Your API key is sent to the backend and
        is not displayed after a successful save.
      </div>


      <div className="form-grid">
        <label>
          <span>Provider</span>

          <input
            type="text"
            placeholder="OpenAI"
            value={provider}
            onChange={(event) =>
              setProvider(
                event.target.value,
              )
            }
          />
        </label>


        <label>
          <span>Model</span>

          <input
            type="text"
            placeholder="gpt-4o-mini"
            value={model}
            onChange={(event) =>
              setModel(
                event.target.value,
              )
            }
          />
        </label>


        <label className="full-width">
          <span>API base URL</span>

          <input
            type="text"
            placeholder="https://api.openai.com/v1"
            value={baseUrl}
            onChange={(event) =>
              setBaseUrl(
                event.target.value,
              )
            }
          />

          <small>
            Use the API root, not the /chat/completions
            endpoint.
          </small>
        </label>


        <label className="full-width">
          <span>API key</span>

          <input
            type="password"
            placeholder="Your API key"
            value={apiKey}
            onChange={(event) =>
              setApiKey(
                event.target.value,
              )
            }
            autoComplete="off"
          />
        </label>
      </div>


      <button
        className="connect-button"
        onClick={saveAI}
        disabled={
          loading ||
          !provider ||
          !apiKey ||
          !baseUrl ||
          !model
        }
      >
        {loading ? (
          <>
            <Loader2
              size={16}
              className="spin"
            />
            Testing...
          </>
        ) : (
          <>
            <Cpu size={16} />
            Save AI provider
          </>
        )}
      </button>


      {error && (
        <div className="result error">
          <XCircle size={18} />

          <div>
            <strong>
              AI configuration failed
            </strong>

            <p>
              {error}
            </p>
          </div>
        </div>
      )}


      {result && (
        <div className="result success">
          <CheckCircle2 size={18} />

          <div>
            <strong>
              AI provider configured
            </strong>

            <p>
              Provider:{" "}
              {result.ai.provider}
            </p>

            <p>
              Model:{" "}
              {result.ai.model}
            </p>

            <p>
              Endpoint:{" "}
              {result.ai.base_url}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}