from fastapi import APIRouter, HTTPException

from app.database.repository import BlogRepository
from app.github.blog_reader import BlogReader
from app.github.client import GitHubError


router = APIRouter()


@router.get("/")
async def get_blogs():
    db = BlogRepository()
    return {
        "blogs": db.published_articles(),
        "count": len(db.published_articles()),
    }


@router.get("/latest")
async def get_latest_blog():
    blogs = BlogRepository().published_articles(limit=1)
    return {"blog": blogs[0] if blogs else None}


@router.get("/inspect")
async def inspect_blog():
    try:
        snapshot = await BlogReader().read()
        return {
            "success": True,
            "path": snapshot.path,
            "sha": snapshot.sha,
            "fields": snapshot.structure.fields,
            "content_format": snapshot.structure.content_format,
            "quote": snapshot.structure.quote,
            "item_indent": snapshot.structure.item_indent,
            "property_indent": snapshot.structure.property_indent,
            "character_count": len(snapshot.content),
        }
    except (GitHubError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
