import asyncio
from datetime import datetime, timezone
from typing import Any

from app.ai.client import AIClient
from app.ai.prompts import (
    ARTICLE_PROMPT,
    SEO_PROMPT,
    STRUCTURE_SYSTEM_PROMPT,
    TOPIC_SELECTION_PROMPT,
)
from app.core.config import get_target_countries
from app.github.blog_formatter import BlogFormatter
from app.github.client import GitHubClient
from app.research.news import NewsResearcher
from app.research.trends import GoogleTrendsService


class PipelineError(Exception):
    pass


class BlogAutomationPipeline:
    def __init__(self) -> None:
        self.ai = AIClient()
        self.github = GitHubClient()
        self.trends = GoogleTrendsService()
        self.news = NewsResearcher()
        self.formatter = BlogFormatter()

    async def run(
        self,
    ) -> dict[str, Any]:
        started = datetime.now(
            timezone.utc
        )

        result: dict[str, Any] = {
            "success": False,
            "started_at": started.isoformat(),
            "stages": [],
        }

        self._stage(
            result,
            "trend_collection",
        )

        candidates = (
            await self._collect_trends()
        )

        if not candidates:
            raise PipelineError(
                "No active technology/science "
                "trend candidates were found."
            )

        result["trend_count"] = len(
            candidates
        )

        self._stage(
            result,
            "github_read",
        )

        blog_file = (
            await self.github.get_file()
        )

        structure = (
            self.formatter.analyze_structure(
                blog_file.content
            )
        )

        existing_titles = structure[
            "sample_titles"
        ]

        result["blog_structure"] = {
            "keys": structure[
                "top_level_keys"
            ],
            "content_types": structure[
                "content_types"
            ],
        }

        self._stage(
            result,
            "topic_selection",
        )

        selected = await self._select_topic(
            candidates,
            existing_titles,
        )

        if not selected:
            raise PipelineError(
                "AI could not select a suitable topic."
            )

        result["selected_topic"] = selected

        self._stage(
            result,
            "source_research",
        )

        sources = await self.news.research(
            selected,
            limit=5,
        )

        result["source_count"] = len(
            sources
        )

        self._stage(
            result,
            "seo_research",
        )

        seo = await self._research_seo(
            selected,
            sources,
        )

        result["seo"] = seo

        self._stage(
            result,
            "article_generation",
        )

        generated = await self._generate_article(
            selected,
            sources,
            seo,
            structure,
        )

        article = (
            self.formatter.build_blog_object(
                generated,
                structure,
            )
        )

        self._validate_article(
            article,
            blog_file.content,
        )

        result["article"] = {
            "title": article.get(
                "title"
            ),
            "slug": article.get(
                "slug"
            ),
            "category": article.get(
                "category"
            ),
        }

        self._stage(
            result,
            "github_publish",
        )

        new_blog_source = (
            self.formatter.insert_article(
                blog_file.content,
                article,
            )
        )

        commit = await self.github.update_file(
            content=new_blog_source,
            sha=blog_file.sha,
            message=(
                "automation: publish "
                f"{article.get('title', 'new article')}"
            ),
        )

        result["commit"] = {
            "sha": commit.get(
                "commit",
                {}
            ).get(
                "sha"
            ),
            "url": commit.get(
                "commit",
                {}
            ).get(
                "html_url"
            ),
        }

        finished = datetime.now(
            timezone.utc
        )

        result["success"] = True
        result["finished_at"] = (
            finished.isoformat()
        )

        return result

    async def _collect_trends(
        self,
    ) -> list[dict[str, Any]]:
        countries = get_target_countries()

        tasks = []

        for country in countries:
            for category in (
                "technology",
                "science",
            ):
                tasks.append(
                    self.trends.get_country_topics(
                        country=country,
                        category=category,
                        hours=24,
                        limit=10,
                    )
                )

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        candidates = []

        for value in results:
            if isinstance(
                value,
                Exception,
            ):
                continue

            candidates.extend(value)

        candidates.sort(
            key=lambda item: (
                item.get(
                    "increase_percentage"
                )
                or 0
            ),
            reverse=True,
        )

        return candidates

    async def _select_topic(
        self,
        candidates: list[dict[str, Any]],
        existing_titles: list[str],
    ) -> dict[str, Any] | None:
        payload = {
            "existing_titles": existing_titles[
                :30
            ],
            "candidates": candidates[
                :40
            ],
        }

        response = await self.ai.generate_json(
            system_prompt=TOPIC_SELECTION_PROMPT,
            user_prompt=(
                "Select exactly one topic.\n\n"
                + self._json(payload)
            ),
            temperature=0.1,
        )

        selected_query = response.get(
            "query"
        )

        if not selected_query:
            return None

        for candidate in candidates:
            if (
                candidate.get("query")
                == selected_query
            ):
                return candidate

        return None

    async def _research_seo(
        self,
        topic: dict[str, Any],
        sources: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = {
            "trend": topic,
            "sources": sources,
        }

        return await self.ai.generate_json(
            system_prompt=SEO_PROMPT,
            user_prompt=(
                "Create the SEO package.\n\n"
                + self._json(payload)
            ),
            temperature=0.2,
        )

    async def _generate_article(
        self,
        topic: dict[str, Any],
        sources: list[dict[str, Any]],
        seo: dict[str, Any],
        structure: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "topic": topic,
            "sources": sources,
            "seo": seo,
            "blog_structure": {
                "top_level_keys": structure[
                    "top_level_keys"
                ],
                "content_types": structure[
                    "content_types"
                ],
                "sample_source": structure[
                    "sample_source"
                ],
            },
        }

        return await self.ai.generate_json(
            system_prompt=ARTICLE_PROMPT,
            user_prompt=(
                "Generate the article now.\n\n"
                + self._json(payload)
            ),
            temperature=0.4,
        )

    def _validate_article(
        self,
        article: dict[str, Any],
        current_blog: str,
    ) -> None:
        title = str(
            article.get(
                "title",
                "",
            )
        ).strip()

        slug = str(
            article.get(
                "slug",
                "",
            )
        ).strip()

        description = str(
            article.get(
                "description",
                "",
            )
        ).strip()

        content = article.get(
            "content"
        )

        if not title:
            raise PipelineError(
                "Generated article has no title."
            )

        if not slug:
            raise PipelineError(
                "Generated article has no slug."
            )

        if not description:
            raise PipelineError(
                "Generated article has no description."
            )

        if not isinstance(
            content,
            list,
        ):
            raise PipelineError(
                "Generated content is not a list."
            )

        if len(content) < 4:
            raise PipelineError(
                "Generated article is too short."
            )

        if (
            f'slug: "{slug}"'
            in current_blog
            or f'"slug": "{slug}"'
            in current_blog
        ):
            raise PipelineError(
                f"Slug already exists: {slug}"
            )

        if title.lower() in (
            current_blog.lower()
        ):
            raise PipelineError(
                "Generated title already "
                "exists in blog.js."
            )

    @staticmethod
    def _stage(
        result: dict[str, Any],
        name: str,
    ) -> None:
        result["stages"].append(
            {
                "name": name,
                "time": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        )

    @staticmethod
    def _json(
        value: Any,
    ) -> str:
        import json

        return json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
        )