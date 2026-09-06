from collections import defaultdict
from typing import Any

from app.database.repository import BlogRepository


class TopicPipeline:
    def __init__(self):
        self.db = BlogRepository()

    def choose(self, topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "countries": [],
                "scores": [],
                "increase": [],
                "items": [],
            }
        )

        for topic in topics:
            key = self.db.trend_key(topic.get("query", ""))
            if not key:
                continue
            bucket = grouped[key]
            bucket["countries"].append(topic.get("country_code"))
            bucket["scores"].append(float(topic.get("final_score") or 0))
            bucket["increase"].append(float(topic.get("increase_percentage") or 0))
            bucket["items"].append(topic)

        candidates = []
        for key, bucket in grouped.items():
            best = max(
                bucket["items"],
                key=lambda x: float(x.get("final_score") or 0),
            ).copy()
            best["trend_key"] = key
            best["country_count"] = len(set(bucket["countries"]))
            best["country_codes"] = sorted(set(bucket["countries"]))
            best["cross_country_score"] = round(
                min(100, best.get("final_score", 0) + max(0, bucket["country_count"] - 1) * 7),
                2,
            )
            best["max_increase_percentage"] = max(bucket["increase"] or [0])
            candidates.append(best)

        candidates.sort(
            key=lambda x: (
                x["cross_country_score"],
                x["country_count"],
                x.get("max_increase_percentage", 0),
            ),
            reverse=True,
        )
        return candidates
