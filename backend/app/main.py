from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.automation import (
    router as automation_router,
)
from app.api.research import (
    router as research_router,
)
from app.api.settings import (
    router as settings_router,
)


app = FastAPI(
    title="Ritnav Blog Engine",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    settings_router,
    prefix="/api/settings",
    tags=["Settings"],
)

app.include_router(
    research_router,
    prefix="/api/research",
    tags=["Research"],
)

app.include_router(
    automation_router,
    prefix="/api/automation",
    tags=["Automation"],
)


@app.get("/")
async def root():
    return {
        "service": "Ritnav Blog Engine",
        "status": "running",
        "version": "0.2.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
    }