"use client";

import { useEffect, useState } from "react";

type Blog = {
  id?: string | number;
  title?: string;
  slug?: string;
  description?: string;
  excerpt?: string;
  category?: string;
  author?: string;
  date?: string;
  published_at?: string;
  created_at?: string;
  updated_at?: string;
  url?: string;
  image?: string;
};

type BlogsResponse = {
  blogs?: Blog[];
  articles?: Blog[];
  items?: Blog[];
  count?: number;
};

export default function ArticlesPage() {
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadBlogs() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        "http://127.0.0.1:8000/api/blogs/",
        {
          method: "GET",
          cache: "no-store",
        }
      );

      const data: BlogsResponse =
        await response.json();

      if (!response.ok) {
        throw new Error(
          `Failed to load articles (${response.status})`
        );
      }

      if (Array.isArray(data.blogs)) {
        setBlogs(data.blogs);
      } else if (Array.isArray(data.articles)) {
        setBlogs(data.articles);
      } else if (Array.isArray(data.items)) {
        setBlogs(data.items);
      } else {
        setBlogs([]);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load articles."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadBlogs();
  }, []);

  function formatDate(value?: string) {
    if (!value) {
      return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleDateString();
  }

  return (
    <main className="articles-page">
      <header className="articles-header">
        <div>
          <span className="page-label">
            Content
          </span>

          <h1>Articles</h1>

          <p>
            Manage and inspect the blogs discovered,
            generated, and published by Ritnav.
          </p>
        </div>

        <button
          type="button"
          onClick={loadBlogs}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </header>

      {error ? (
        <div className="error-box">
          <strong>
            Unable to load articles
          </strong>

          <span>{error}</span>
        </div>
      ) : null}

      <section className="articles-container">
        <div className="section-header">
          <div>
            <h2>Published articles</h2>
            <p>
              {blogs.length} article
              {blogs.length === 1 ? "" : "s"}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state">
            Loading articles...
          </div>
        ) : blogs.length === 0 ? (
          <div className="empty-state">
            <h3>No articles found</h3>

            <p>
              Your connected blog repository has not
              returned any articles yet.
            </p>
          </div>
        ) : (
          <div className="articles-grid">
            {blogs.map((blog, index) => {
              const key =
                blog.id ??
                blog.slug ??
                `${blog.title ?? "article"}-${index}`;

              return (
                <article
                  className="article-card"
                  key={key}
                >
                  <div className="article-card-content">
                    <div className="article-category">
                      {blog.category ||
                        "Technology"}
                    </div>

                    <h3>
                      {blog.title ||
                        "Untitled article"}
                    </h3>

                    <p>
                      {blog.description ||
                        blog.excerpt ||
                        "No description available."}
                    </p>

                    <div className="article-meta">
                      {blog.author ? (
                        <span>
                          By {blog.author}
                        </span>
                      ) : null}

                      {(blog.published_at ||
                        blog.date ||
                        blog.created_at) ? (
                        <span>
                          {formatDate(
                            blog.published_at ||
                              blog.date ||
                              blog.created_at
                          )}
                        </span>
                      ) : null}
                    </div>
                  </div>

                  {blog.url ? (
                    <a
                      href={blog.url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open article
                    </a>
                  ) : null}
                </article>
              );
            })}
          </div>
        )}
      </section>

      <style jsx>{`
        .articles-page {
          max-width: 1280px;
          margin: 0 auto;
          padding: 32px;
        }

        .articles-header {
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
          gap: 24px;
          margin-bottom: 28px;
        }

        .page-label {
          display: block;
          margin-bottom: 8px;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          opacity: 0.55;
        }

        .articles-header h1 {
          margin: 0;
          font-size: 34px;
          line-height: 1.1;
        }

        .articles-header p {
          margin: 10px 0 0;
          max-width: 620px;
          opacity: 0.68;
        }

        .articles-header button {
          border: 0;
          border-radius: 10px;
          padding: 10px 16px;
          cursor: pointer;
        }

        .articles-header button:disabled {
          opacity: 0.6;
          cursor: wait;
        }

        .error-box {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin-bottom: 20px;
          padding: 16px;
          border-radius: 12px;
          border: 1px solid rgba(
            255,
            80,
            80,
            0.35
          );
        }

        .articles-container {
          overflow: hidden;
          border-radius: 16px;
          border: 1px solid
            rgba(128, 128, 128, 0.18);
        }

        .section-header {
          padding: 20px;
          border-bottom: 1px solid
            rgba(128, 128, 128, 0.14);
        }

        .section-header h2 {
          margin: 0;
          font-size: 19px;
        }

        .section-header p {
          margin: 5px 0 0;
          font-size: 13px;
          opacity: 0.6;
        }

        .articles-grid {
          display: grid;
          grid-template-columns:
            repeat(
              auto-fit,
              minmax(280px, 1fr)
            );
          gap: 16px;
          padding: 20px;
        }

        .article-card {
          display: flex;
          min-height: 220px;
          flex-direction: column;
          justify-content: space-between;
          gap: 20px;
          padding: 20px;
          border-radius: 14px;
          border: 1px solid
            rgba(128, 128, 128, 0.15);
        }

        .article-category {
          margin-bottom: 10px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          opacity: 0.55;
        }

        .article-card h3 {
          margin: 0;
          font-size: 20px;
          line-height: 1.25;
        }

        .article-card p {
          margin: 12px 0 0;
          line-height: 1.6;
          opacity: 0.7;
        }

        .article-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          margin-top: 16px;
          font-size: 12px;
          opacity: 0.55;
        }

        .article-card > a {
          align-self: flex-start;
          font-size: 13px;
          font-weight: 600;
        }

        .empty-state {
          padding: 60px 20px;
          text-align: center;
          opacity: 0.7;
        }

        .empty-state h3 {
          margin: 0;
        }

        .empty-state p {
          margin: 8px 0 0;
        }

        @media (max-width: 720px) {
          .articles-page {
            padding: 20px;
          }

          .articles-header {
            align-items: flex-start;
            flex-direction: column;
          }
        }
      `}</style>
    </main>
  );
}