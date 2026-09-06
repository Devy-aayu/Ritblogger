from typing import Any

from app.database.repository import BlogRepository
from app.github.blog_reader import BlogReader
from app.github.blog_updater import BlogUpdater


class PublishPipeline:
    def __init__(self):
        self.db = BlogRepository()
        self.reader = BlogReader()
        self.updater = BlogUpdater()

    async def publish(
        self,
        topic: dict[str, Any],
        article: dict[str, Any],
        research: dict[str, Any],
    ) -> dict[str, Any]:
        # Re-read immediately before publishing so a stale SHA cannot overwrite
        # a human's GitHub change made while AI generation was running.
        snapshot = await self.reader.read()

        if self.db.article_exists(
            article["title"],
            article["slug"],
            article["content"],
        ):
            raise ValueError("Duplicate detected immediately before publish.")

        result = await self.updater.publish(snapshot, article)

        self.db.record_article(
            title=article["title"],
            slug=article["slug"],
            primary_keyword=article["primary_keyword"],
            content=article["content"],
            trend_key=topic["trend_key"],
            country=",".join(topic.get("country_codes", [])),
            category=article["category"],
            status="published",
            research=research,
        )

        return {
            "github": {
                "commit_sha": result.get("commit", {}).get("sha"),
                "commit_url": result.get("commit", {}).get("html_url"),
            },
            "article": article,
        }
