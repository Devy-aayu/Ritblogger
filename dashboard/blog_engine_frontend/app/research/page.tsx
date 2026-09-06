"use client";

import { useEffect, useState } from "react";
import {
  ExternalLink,
  Flame,
  Globe2,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import { apiGet } from "../../lib/api";

type TrendCategory = {
  id?: number;
  name?: string;
};

type TrendItem = {
  position?: number;
  query: string;
  normalized_query?: string;
  search_volume?: number;
  search_volume_label?: string;
  increase_percentage?: number;
  started_at?: string;
  ended_at?: string;
  active?: boolean;
  trend_breakdown?: string[];
  categories?: TrendCategory[];
  explore_url?: string;
  source?: string;
  country_code: string;
  country_name: string;
};

type TrendsResponse = {
  success: boolean;
  category: string;
  hours: number;
  count: number;
  countries: string[];
  topics: TrendItem[];
};

const categories = [
  {
    label: "Technology",
    value: "technology",
    icon: Sparkles,
  },
  {
    label: "Science",
    value: "science",
    icon: Globe2,
  },
];

const countryFlags: Record<string, string> = {
  US: "🇺🇸",
  GB: "🇬🇧",
  CA: "🇨🇦",
  AU: "🇦🇺",
  IN: "🇮🇳",
};

export default function ResearchPage() {
  const [category, setCategory] = useState("technology");

  const [topics, setTopics] = useState<TrendItem[]>([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [lastUpdated, setLastUpdated] =
    useState<Date | null>(null);

  async function loadTrends(
    selectedCategory = category,
  ) {
    setLoading(true);
    setError("");

    try {
      const encodedCategory =
        encodeURIComponent(selectedCategory);

      const data = await apiGet<TrendsResponse>(
        `/api/research/trends?category=${encodedCategory}&hours=24&limit=25`,
      );

      setTopics(data.topics || []);

      setLastUpdated(new Date());
    } catch (err) {
      setTopics([]);

      setError(
        err instanceof Error
          ? err.message
          : "Could not load Google Trends.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTrends("technology");
  }, []);

  function changeCategory(
    selectedCategory: string,
  ) {
    setCategory(selectedCategory);
    loadTrends(selectedCategory);
  }

  return (
    <main className="research-page">
      <header className="research-header">
        <div>
          <div className="page-label">
            Research Engine
          </div>

          <h1>Trending Topics</h1>

          <p>
            Live Google Trends across your target
            markets, filtered by category.
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={() => loadTrends()}
          disabled={loading}
        >
          <RefreshCw
            size={16}
            className={
              loading ? "spin" : ""
            }
          />

          {loading
            ? "Scanning..."
            : "Refresh trends"}
        </button>
      </header>

      <section className="research-controls">
        <div className="category-tabs">
          {categories.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.value}
                className={
                  category === item.value
                    ? "category-tab active"
                    : "category-tab"
                }
                onClick={() =>
                  changeCategory(
                    item.value,
                  )
                }
              >
                <Icon size={15} />

                {item.label}
              </button>
            );
          })}
        </div>

        <div className="research-meta">
          <span>
            5 target countries
          </span>

          <span>•</span>

          <span>
            Past 24 hours
          </span>

          {lastUpdated && (
            <>
              <span>•</span>

              <span>
                Updated{" "}
                {lastUpdated.toLocaleTimeString(
                  [],
                  {
                    hour: "2-digit",
                    minute: "2-digit",
                  },
                )}
              </span>
            </>
          )}
        </div>
      </section>

      {error && (
        <div className="research-error">
          <strong>
            Trend request failed
          </strong>

          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="research-loading">
          <RefreshCw
            size={22}
            className="spin"
          />

          <span>
            Fetching live Google Trends...
          </span>
        </div>
      )}

      {!loading &&
        !error &&
        topics.length === 0 && (
          <div className="research-empty">
            <Flame size={30} />

            <h2>
              No trends found
            </h2>

            <p>
              Google Trends returned no matching
              topics for this category.
            </p>
          </div>
        )}

      {!loading &&
        topics.length > 0 && (
          <section className="trend-grid">
            {topics.map(
              (topic, index) => (
                <TrendCard
                  key={`${topic.country_code}-${topic.query}-${index}`}
                  topic={topic}
                  index={index}
                />
              ),
            )}
          </section>
        )}
    </main>
  );
}


function TrendCard({
  topic,
  index,
}: {
  topic: TrendItem;
  index: number;
}) {
  const flag =
    countryFlags[topic.country_code] ||
    "🌐";

  const categoryName =
    topic.categories?.[0]?.name ||
    "Trend";

  const volume =
    topic.search_volume_label ||
    formatNumber(
      topic.search_volume,
    );

  return (
    <article className="trend-card">
      <div className="trend-top">
        <span className="trend-rank">
          #{index + 1}
        </span>

        <span className="trend-country">
          {flag} {topic.country_name}
        </span>
      </div>

      <div className="trend-category-row">
        <span className="trend-category">
          {categoryName}
        </span>

        {topic.active && (
          <span className="active-badge">
            Active
          </span>
        )}
      </div>

      <h2 className="trend-title">
        {topic.query}
      </h2>

      <div className="trend-source">
        {topic.source ||
          "Google Trends"}
      </div>

      <div className="trend-stats">
        <div className="trend-stat">
          <span>Searches</span>

          <strong>
            {volume || "—"}
          </strong>
        </div>

        <div className="trend-stat">
          <span>Increase</span>

          <strong>
            {topic.increase_percentage !=
              null
              ? `+${topic.increase_percentage}%`
              : "—"}
          </strong>
        </div>

        <div className="trend-stat">
          <span>Position</span>

          <strong>
            {topic.position ??
              topic.rank ??
              index + 1}
          </strong>
        </div>
      </div>

      <div className="trend-footer">
        <div className="trend-time">
          {topic.started_at
            ? formatDate(topic.started_at)
            : "Currently trending"}
        </div>

        {topic.explore_url && (
          <a
            href={topic.explore_url}
            target="_blank"
            rel="noopener noreferrer"
            className="trend-link"
          >
            Explore
            <ExternalLink
              size={13}
            />
          </a>
        )}
      </div>
    </article>
  );
}


function formatNumber(
  value?: number,
) {
  if (
    value === undefined ||
    value === null
  ) {
    return "";
  }

  return new Intl.NumberFormat(
    "en",
    {
      notation: "compact",
      maximumFractionDigits: 1,
    },
  ).format(value);
}


function formatDate(
  value: string,
) {
  const date = new Date(value);

  if (
    Number.isNaN(date.getTime())
  ) {
    return "Currently trending";
  }

  return date.toLocaleString(
    [],
    {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    },
  );
}