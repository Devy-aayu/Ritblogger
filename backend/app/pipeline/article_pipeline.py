import re
from typing import Any

from app.ai.writer import ArticleWriter
from app.database.repository import BlogRepository
from app.github.blog_reader import BlogReader
from app.github.blog_formatter import extract_existing_values
from app.research.seo import SEOResearcher
from app.research.search import build_structure_summary


def _tokens(text: str) -> set[str]:
    return {
        word for word in re.findall(r"[a-z0-9]+", (text or "").lower())
        if len(word) > 2
    }


class ArticlePipeline:
    def __init__(self):
        self.db = BlogRepository()
        self.reader = BlogReader()
        self.seo = SEOResearcher()
        self.writer = ArticleWriter()

    async def run(self, topic: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        snapshot = await self.reader.read()
        titles = self.db.recent_titles(250)
        existing_file_values = extract_existing_values(
            snapshot.content,
            snapshot.structure.fields,
        )
        existing_titles = existing_file_values.get("title", [])
        for title in existing_titles:
            if title not in titles:
                titles.append(title)

        research = await self.seo.research(
            topic,
            titles,
            snapshot.structure.content_format,
        )

        if not bool(research.get("publish")):
            raise ValueError(
                f"Trend rejected by research gate: "
                f"{research.get('reason', 'not suitable')}"
            )

        seo_score = float(research.get("seo_score") or 0)
        quality_score = float(research.get("trend_quality_score") or 0)
        novelty_score = float(research.get("novelty_score") or 0)

        if seo_score < 55 or quality_score < 55 or novelty_score < 50:
            raise ValueError(
                "Trend did not pass the minimum editorial gate "
                f"(SEO={seo_score}, quality={quality_score}, novelty={novelty_score})."
            )

        structure_summary = build_structure_summary(snapshot.structure)
        article = await self.writer.write(
            topic,
            research,
            structure_summary,
        )

        self._validate_article(article, research)

        existing_rows = self.db.all_title_slug_keyword_rows()
        existing_rows.extend(
            {"title": title, "slug": "", "primary_keyword": ""}
            for title in existing_titles
            if not any(
                self.db.normalize(title) == self.db.normalize(row.get("title") or "")
                for row in existing_rows
            )
        )
        new_title_tokens = _tokens(article["title"])
        primary = _tokens(article["primary_keyword"])

        for row in existing_rows:
            old_title = _tokens(row.get("title") or "")
            old_keyword = _tokens(row.get("primary_keyword") or "")
            if new_title_tokens and old_title:
                overlap = len(new_title_tokens & old_title) / max(
                    1, len(new_title_tokens | old_title)
                )
                if overlap >= 0.72:
                    raise ValueError(
                        f"Article is too similar to existing title: {row.get('title')}"
                    )
            if primary and old_keyword and len(primary & old_keyword) >= 2:
                raise ValueError(
                    f"Primary keyword overlaps an existing article too closely: "
                    f"{row.get('primary_keyword')}"
                )

        if self.db.similar_topic_recently_used(
            topic["trend_key"],
            days=30,
        ):
            raise ValueError(
                "This trend was already used recently. Waiting for a genuinely new angle."
            )

        if self.db.article_exists(
            article["title"],
            article["slug"],
            article["content"],
        ):
            raise ValueError("Duplicate article detected.")

        article["category"] = (
            "Science"
            if str(topic.get("category", "")).lower() == "science"
            else "Technology"
        )

        return article, research

    @staticmethod
    def _validate_article(article: dict[str, Any], research: dict[str, Any]):
        required = [
            "title",
            "slug",
            "excerpt",
            "content",
            "category",
            "tags",
            "seo_title",
            "meta_description",
            "primary_keyword",
            "secondary_keywords",
            "faq",
            "read_time",
        ]
        missing = [key for key in required if not article.get(key) and key != "tags"]
        if missing:
            raise ValueError("AI returned incomplete article data: " + ", ".join(missing))

        slug = article["slug"].strip().lower()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError("AI generated an invalid slug.")

        if len(article["meta_description"].strip()) > 170:
            raise ValueError("Meta description is too long.")

        if len(article["primary_keyword"].strip()) < 2:
            raise ValueError("Primary keyword is empty.")

        word_count = len(re.findall(r"\b\w+\b", article["content"]))
        if word_count < 700:
            raise ValueError(
                f"Generated article is too short ({word_count} words)."
            )
