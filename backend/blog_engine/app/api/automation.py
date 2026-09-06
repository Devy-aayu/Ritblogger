from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def automation_status():
    return {
        "enabled": False,
        "status": "idle",
        "message": "Automation engine is not configured yet.",
    }


@router.post("/run")
async def run_automation():
    return {
        "success": False,
        "message": "Automation pipeline will be connected in the next step.",
    }


@router.post("/pause")
async def pause_automation():
    return {
        "success": True,
        "status": "paused",
    }