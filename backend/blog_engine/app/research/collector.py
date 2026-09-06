from typing import Any

from app.research.trends import GoogleTrendsService


class ResearchCollector:
    def __init__(self):
        self.trends = GoogleTrendsService()

    async def collect(
        self,
        category: str = "technology",
        hours: int = 24,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        return await self.trends.get_all_countries(
            category=category,
            hours=hours,
            limit=limit,
        )