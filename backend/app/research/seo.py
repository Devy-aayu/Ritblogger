from typing import Any

from app.ai.client import GeminiClient
from app.ai.prompts import build_research_prompt


class SEOResearcher:
    def __init__(self):
        self.ai = GeminiClient()

    async def research(
        self,
        topic: dict[str, Any],
        existing_titles: list[str],
        content_format: str,
    ) -> dict[str, Any]:
        return await self.ai.research(
            build_research_prompt(
                topic,
                existing_titles,
                content_format,
            )
        )
