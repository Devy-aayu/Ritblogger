from fastapi import APIRouter, HTTPException, Query

from app.research.collector import ResearchCollector
from app.research.trends import TrendsError


router = APIRouter()


VALID_CATEGORIES = {
    "technology",
    "science",
}


@router.get("/trends")
async def get_trends(
    category: str = Query(
        default="technology",
    ),
    hours: int = Query(
        default=24,
        ge=4,
        le=168,
    ),
    limit: int = Query(
        default=25,
        ge=1,
        le=100,
    ),
):
    category = category.lower()

    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Category must be "
                "'technology' or 'science'."
            ),
        )

    collector = ResearchCollector()

    try:
        topics = await collector.collect(
            category=category,
            hours=hours,
            limit=limit,
        )

        topics.sort(
            key=lambda item: (
                item.get("search_volume") or 0
            ),
            reverse=True,
        )

        return {
            "success": True,
            "category": category,
            "hours": hours,
            "count": len(topics),
            "countries": [
                "US",
                "GB",
                "CA",
                "AU",
                "IN",
            ],
            "topics": topics,
        }

    except TrendsError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc