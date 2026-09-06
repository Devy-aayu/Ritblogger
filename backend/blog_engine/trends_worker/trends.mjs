import {
  fetchTrendingNow
} from "google-trends-now";

const args = process.argv.slice(2);

function getArg(name, fallback) {
  const index = args.indexOf(name);

  if (index === -1) {
    return fallback;
  }

  return args[index + 1] ?? fallback;
}

const geo = getArg("--geo", "US").toUpperCase();
const category = getArg("--category", "all").toLowerCase();
const hours = Number(getArg("--hours", "24"));
const limit = Number(getArg("--limit", "25"));

try {
  const result = await fetchTrendingNow({
    geo,
    hours,
    category,
    status: "active",
    sort: "relevance",
    limit,
    fallback: "none",
  });

  if (
    result.fetch_status !== "success" ||
    !Array.isArray(result.items)
  ) {
    console.error(
      JSON.stringify({
        success: false,
        error:
          result.error ||
          "Google Trends returned no usable data.",
        fetch_status: result.fetch_status,
        source: result.source,
      })
    );

    process.exit(1);
  }

  const items = result.items.map((item) => ({
    position: item.position,
    query: item.query,
    normalized_query: item.normalized_query,
    search_volume: item.search_volume,
    search_volume_label: item.search_volume_label,
    increase_percentage: item.increase_percentage,
    started_at: item.started_at,
    ended_at: item.ended_at,
    active: item.active,
    trend_breakdown: item.trend_breakdown || [],
    categories: item.categories || [],
    explore_url: item.explore_url,
    source: item.source,
  }));

  console.log(
    JSON.stringify({
      success: true,
      geo,
      hours,
      category,
      source: result.source,
      source_url: result.source_url,
      observed_at: result.observed_at,
      count: items.length,
      items,
    })
  );
} catch (error) {
  console.error(
    JSON.stringify({
      success: false,
      error:
        error instanceof Error
          ? error.message
          : String(error),
    })
  );

  process.exit(1);
}