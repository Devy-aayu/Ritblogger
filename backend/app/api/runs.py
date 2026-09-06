from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_runs():
    return {
        "runs": [],
        "count": 0,
    }

