"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Github,
  Loader2,
  XCircle,
} from "lucide-react";

import { apiPost } from "../../lib/api";

type GitHubResult = {
  success: boolean;
  message: string;

  account: {
    login: string;
    name: string | null;
  };

  repository: {
    full_name: string;
    private: boolean;
    default_branch: string;
    url: string;
  };

  blog: {
    path: string;
    sha: string;
    length: number;
  };
};

export default function GitHubSetup() {
  const [token, setToken] = useState("");
  const [owner, setOwner] = useState("");
  const [repository, setRepository] = useState("");
  const [branch, setBranch] = useState("main");
  const [blogPath, setBlogPath] = useState("");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GitHubResult | null>(
    null,
  );
  const [error, setError] = useState("");

  async function connect() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await apiPost<GitHubResult>(
        "/api/settings/github/connect",
        {
          token: token.trim(),
          owner: owner.trim(),
          repository: repository.trim(),
          branch: branch.trim(),
          blog_path: blogPath.trim(),
        },
      );

      setResult(data);

      setToken("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not connect to GitHub.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="setup-card">
      <div className="setup-heading">
        <div className="setup-icon">
          <Github size={22} />
        </div>

        <div>
          <h2>Connect GitHub</h2>

          <p>
            Connect your Ritnav repository and locate the
            blog.js file.
          </p>
        </div>
      </div>

      <div className="setup-warning">
        Your GitHub token is sent to the backend and is never
        displayed after a successful connection. Do not commit
        your token to GitHub.
      </div>

      <div className="form-grid">
        <label>
          <span>GitHub token</span>

          <input
            type="password"
            placeholder="github_pat_..."
            value={token}
            onChange={(event) =>
              setToken(event.target.value)
            }
            autoComplete="off"
          />
        </label>

        <label>
          <span>GitHub username / owner</span>

          <input
            type="text"
            placeholder="Devy-aayu"
            value={owner}
            onChange={(event) =>
              setOwner(event.target.value)
            }
          />
        </label>

        <label>
          <span>Repository</span>

          <input
            type="text"
            placeholder="Aikyara"
            value={repository}
            onChange={(event) =>
              setRepository(event.target.value)
            }
          />
        </label>

        <label>
          <span>Branch</span>

          <input
            type="text"
            placeholder="main"
            value={branch}
            onChange={(event) =>
              setBranch(event.target.value)
            }
          />
        </label>

        <label className="full-width">
          <span>blog.js path</span>

          <input
            type="text"
            placeholder="lib/blogs.js"
            value={blogPath}
            onChange={(event) =>
              setBlogPath(event.target.value)
            }
          />

          <small>
            Example: lib/blogs.js
          </small>
        </label>
      </div>

      <button
        className="connect-button"
        onClick={connect}
        disabled={
          loading ||
          !token ||
          !owner ||
          !repository ||
          !branch ||
          !blogPath
        }
      >
        {loading ? (
          <>
            <Loader2
              size={16}
              className="spin"
            />
            Connecting...
          </>
        ) : (
          <>
            <Github size={16} />
            Connect repository
          </>
        )}
      </button>

      {error && (
        <div className="result error">
          <XCircle size={18} />

          <div>
            <strong>Connection failed</strong>

            <p>{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="result success">
          <CheckCircle2 size={18} />

          <div>
            <strong>
              GitHub connected successfully
            </strong>

            <p>
              Account:{" "}
              <strong>
                {result.account.login}
              </strong>
            </p>

            <p>
              Repository:{" "}
              <strong>
                {result.repository.full_name}
              </strong>
            </p>

            <p>
              Branch:{" "}
              <strong>
                {result.repository.default_branch}
              </strong>
            </p>

            <p>
              Repository type:{" "}
              <strong>
                {result.repository.private
                  ? "Private"
                  : "Public"}
              </strong>
            </p>

            <p>
              Blog file:{" "}
              <strong>
                {result.blog.path}
              </strong>
            </p>

            <p>
              File size:{" "}
              <strong>
                {result.blog.length.toLocaleString()}
              </strong>{" "}
              characters
            </p>
          </div>
        </div>
      )}
    </div>
  );
}