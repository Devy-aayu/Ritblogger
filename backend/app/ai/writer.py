from typing import Any

from app.ai.client import GeminiClient
from app.ai.prompts import build_article_prompt, build_article_system


class ArticleWriter:
    def __init__(self):
        self.client = GeminiClient()

    async def write(
        self,
        topic: dict[str, Any],
        research: dict[str, Any],
        structure_summary: str,
    ) -> dict[str, Any]:
        return await self.client.generate_article(
            build_article_prompt(topic, research, structure_summary),
            build_article_system(
                structure_summary.split("content_format=")[-1].splitlines()[0]
                if "content_format=" in structure_summary
                else "markdown"
            ),
        )
