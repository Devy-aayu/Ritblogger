from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_blogs():
    return {
        "blogs": [],
        "count": 0,
    }


@router.get("/latest")
async def get_latest_blog():
    return {
        "blog": None,
    }