from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.automation import router as automation_router
from app.api.blogs import router as blogs_router
from app.api.research import router as research_router
from app.api.runs import router as runs_router
from app.api.settings import router as settings_router
from app.core.config import settings
from app.core.logger import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


app = FastAPI(
    title="Ritnav Blog Engine",
    description="Automated trend research, SEO article generation and GitHub publishing engine for Ritnav.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(automation_router, prefix="/api/automation", tags=["Automation"])
app.include_router(blogs_router, prefix="/api/blogs", tags=["Blogs"])
app.include_router(research_router, prefix="/api/research", tags=["Research"])
app.include_router(runs_router, prefix="/api/runs", tags=["Runs"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
app.include_router(settings_router,prefix="/api/settings",)
app.include_router(research_router, prefix="/api/research",)
@app.get("/")
async def root():
    return {
        "name": "Ritnav Blog Engine",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ritnav-blog-engine",
    }