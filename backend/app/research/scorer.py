import re
from typing import Any


TECHNOLOGY_KEYWORDS = {
    "ai",
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "llm",
    "chatgpt",
    "openai",
    "gemini",
    "claude",
    "copilot",
    "nvidia",
    "amd",
    "intel",
    "qualcomm",
    "processor",
    "cpu",
    "gpu",
    "chip",
    "semiconductor",
    "computer",
    "computing",
    "software",
    "hardware",
    "programming",
    "python",
    "javascript",
    "typescript",
    "linux",
    "windows",
    "android",
    "iphone",
    "ios",
    "google",
    "microsoft",
    "apple",
    "samsung",
    "robot",
    "robotics",
    "drone",
    "cybersecurity",
    "cyber security",
    "malware",
    "ransomware",
    "hacker",
    "internet",
    "browser",
    "web",
    "app",
    "application",
    "technology",
    "tech",
    "quantum",
    "cloud",
    "database",
    "api",
    "developer",
    "coding",
    "5g",
    "6g",
    "vr",
    "ar",
    "xr",
    "smartphone",
    "laptop",
    "server",
    "datacenter",
    "data center",
}


SCIENCE_KEYWORDS = {
    "science",
    "scientist",
    "research",
    "study",
    "discovery",
    "physics",
    "chemistry",
    "biology",
    "biotechnology",
    "genetics",
    "dna",
    "rna",
    "genome",
    "astronomy",
    "astrophysics",
    "cosmology",
    "space",
    "nasa",
    "esa",
    "isro",
    "rocket",
    "satellite",
    "moon",
    "lunar",
    "mars",
    "planet",
    "exoplanet",
    "black hole",
    "galaxy",
    "star",
    "supernova",
    "telescope",
    "jwst",
    "james webb",
    "earth",
    "climate",
    "climate change",
    "environment",
    "ecology",
    "ocean",
    "medicine",
    "medical",
    "cancer",
    "vaccine",
    "virus",
    "bacteria",
    "evolution",
    "fossil",
    "geology",
    "neuroscience",
    "nanotechnology",
}


def normalize(text: str) -> str:
    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s\-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


class TopicScorer:

    def _build_search_text(
        self,
        topic: dict[str, Any],
    ) -> str:
        parts = [
            topic.get("title", ""),
            topic.get("query", ""),
            topic.get("category", ""),
        ]
        for category_item in topic.get("categories", []) or []:
            if isinstance(category_item, dict):
                parts.append(category_item.get("name", "") or "")
            elif isinstance(category_item, str):
                parts.append(category_item)

        for news in topic.get(
            "news_items",
            [],
        ):
            parts.append(
                news.get("title") or ""
            )

            parts.append(
                news.get("snippet") or ""
            )

            parts.append(
                news.get("source") or ""
            )

        return normalize(
            " ".join(parts)
        )

    def _count_hits(
        self,
        text: str,
        keywords: set[str],
    ) -> int:
        return sum(
            1
            for keyword in keywords
            if keyword in text
        )

    def classify(
        self,
        topic: dict[str, Any],
    ) -> tuple[str | None, int, int]:
        text = self._build_search_text(
            topic
        )

        tech_hits = self._count_hits(
            text,
            TECHNOLOGY_KEYWORDS,
        )

        science_hits = self._count_hits(
            text,
            SCIENCE_KEYWORDS,
        )

        if tech_hits == 0 and science_hits == 0:
            return None, 0, 0

        if tech_hits > science_hits:
            return (
                "Technology",
                tech_hits,
                science_hits,
            )

        if science_hits > tech_hits:
            return (
                "Science",
                tech_hits,
                science_hits,
            )

        if tech_hits > 0:
            return (
                "Technology",
                tech_hits,
                science_hits,
            )

        return (
            None,
            tech_hits,
            science_hits,
        )

    def score(
        self,
        topic: dict[str, Any],
    ) -> dict[str, Any] | None:
        category, tech_hits, science_hits = (
            self.classify(topic)
        )

        if category is None:
            return None

        try:
            rank = int(
                topic.get(
                    "position",
                    topic.get("rank", 100),
                )
            )
        except (TypeError, ValueError):
            rank = 100

        trend_score = max(
            20,
            100 - ((rank - 1) * 7),
        )

        keyword_hits = max(
            tech_hits,
            science_hits,
        )

        relevance_score = min(
            100,
            keyword_hits * 18,
        )

        news_score = min(
            100,
            len(
                topic.get(
                    "news_items",
                    [],
                )
            ) * 20,
        )

        final_score = round(
            (
                trend_score * 0.45
                + relevance_score * 0.35
                + news_score * 0.20
            ),
            2,
        )

        return {
            **topic,
            "category": category,
            "technology_hits": tech_hits,
            "science_hits": science_hits,
            "trend_score": trend_score,
            "relevance_score": relevance_score,
            "news_score": news_score,
            "final_score": final_score,
        }

    def filter_and_rank(
        self,
        topics: list[dict[str, Any]],
        category: str = "all",
    ) -> list[dict[str, Any]]:
        category = category.lower()

        scored: list[
            dict[str, Any]
        ] = []

        for topic in topics:
            result = self.score(topic)

            if result is None:
                continue

            if category == "all":
                scored.append(result)

            elif (
                category == "technology"
                and result["category"]
                == "Technology"
            ):
                scored.append(result)

            elif (
                category == "science"
                and result["category"]
                == "Science"
            ):
                scored.append(result)

        unique: dict[
            str,
            dict[str, Any],
        ] = {}

        for topic in scored:
            key = normalize(
                topic["title"]
            )

            if key not in unique:
                unique[key] = topic

        return sorted(
            unique.values(),
            key=lambda item: item[
                "final_score"
            ],
            reverse=True,
        )