from fastapi import APIRouter

from app.core.scheduler import (
    AutomationScheduler,
)
from app.services.automation_service import (
    AutomationService,
)


router = APIRouter()

service = AutomationService()
scheduler = AutomationScheduler(
    service
)


@router.get("/status")
async def status():
    return service.status()


@router.post("/run")
async def run_now():
    return await service.run_cycle()


@router.post("/start")
async def start():
    await scheduler.start()

    return {
        "success": True,
        "message": (
            "Automation started. "
            "The first cycle begins now."
        ),
        **service.status(),
    }


@router.post("/stop")
async def stop():
    await scheduler.stop()

    return {
        "success": True,
        "message": "Automation stopped.",
        **service.status(),
    }