from typing import Any

import httpx
from bs4 import BeautifulSoup


class NewsResearcher:
    async def research(
        self,
        topic: dict[str, Any],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        news_items = topic.get(
            "trend_breakdown",
            [],
        )

        if not news_items:
            news_items = topic.get(
                "news_items",
                [],
            )

        results = []

        for item in news_items[:limit]:
            if isinstance(item, str):
                results.append(
                    {
                        "title": item,
                        "url": "",
                        "source": "",
                        "text": "",
                    }
                )
                continue

            url = item.get(
                "url"
            ) or item.get(
                "news_item_url"
            )

            title = item.get(
                "title"
            ) or item.get(
                "news_item_title"
            )

            source = item.get(
                "source"
            ) or item.get(
                "news_item_source"
            )

            snippet = item.get(
                "snippet"
            ) or item.get(
                "news_item_snippet"
            )

            page_text = ""

            if url:
                page_text = await self._fetch_page(
                    url
                )

            results.append(
                {
                    "title": title,
                    "url": url,
                    "source": source,
                    "snippet": snippet,
                    "text": page_text[:8000],
                }
            )

        return results

    async def _fetch_page(
        self,
        url: str,
    ) -> str:
        try:
            async with httpx.AsyncClient(
                timeout=15,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "Chrome/151.0 Safari/537.36"
                    )
                },
            ) as client:
                response = await client.get(
                    url
                )

            if response.status_code != 200:
                return ""

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            for element in soup(
                [
                    "script",
                    "style",
                    "noscript",
                    "svg",
                ]
            ):
                element.decompose()

            paragraphs = [
                element.get_text(
                    " ",
                    strip=True,
                )
                for element in soup.find_all(
                    "p"
                )
            ]

            return "\n".join(
                paragraph
                for paragraph in paragraphs
                if paragraph
            )

        except Exception:
            return ""