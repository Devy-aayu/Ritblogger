from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.github.client import GitHubClient, GitHubError


router = APIRouter()


class GitHubConfigRequest(BaseModel):
    token: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    repository: str = Field(min_length=1)
    branch: str = "main"
    blog_path: str = Field(min_length=1)


class AIConfigRequest(BaseModel):
    provider: str = Field(min_length=1)
    api_key: str = Field(min_length=1)
    base_url: str = Field(min_length=1)
    model: str = Field(min_length=1)


@router.get("/")
async def get_settings():
    return {
        "github": {
            "configured": bool(
                settings.github_token
                and settings.github_owner
                and settings.github_repository
                and settings.github_blog_path
            ),
            "owner": settings.github_owner,
            "repository": settings.github_repository,
            "branch": settings.github_branch,
            "blog_path": settings.github_blog_path,
        },
        "ai": {
            "configured": bool(
                settings.ai_api_key
                and settings.ai_base_url
                and settings.ai_model
            ),
            "provider": settings.ai_provider,
            "base_url": settings.ai_base_url,
            "model": settings.ai_model,
        },
    }


@router.post("/github/connect")
async def connect_github(
    config: GitHubConfigRequest,
):
    old_values = {
        "token": settings.github_token,
        "owner": settings.github_owner,
        "repository": settings.github_repository,
        "branch": settings.github_branch,
        "blog_path": settings.github_blog_path,
    }

    settings.github_token = config.token.strip()
    settings.github_owner = config.owner.strip()
    settings.github_repository = (
        config.repository.strip()
    )
    settings.github_branch = (
        config.branch.strip() or "main"
    )
    settings.github_blog_path = (
        config.blog_path.strip()
        .lstrip("/")
    )

    try:
        github = GitHubClient()

        user = (
            await github.get_current_user()
        )

        repository = (
            await github.get_repository()
        )

        blog = await github.get_file()

        return {
            "success": True,
            "message": (
                "GitHub connected successfully."
            ),
            "account": {
                "login": user.get("login"),
                "name": user.get("name"),
            },
            "repository": {
                "full_name": repository.get(
                    "full_name"
                ),
                "private": repository.get(
                    "private"
                ),
                "default_branch": repository.get(
                    "default_branch"
                ),
                "url": repository.get(
                    "html_url"
                ),
            },
            "blog": {
                "path": blog.path,
                "sha": blog.sha,
                "length": len(blog.content),
            },
        }

    except GitHubError as exc:
        settings.github_token = (
            old_values["token"]
        )
        settings.github_owner = (
            old_values["owner"]
        )
        settings.github_repository = (
            old_values["repository"]
        )
        settings.github_branch = (
            old_values["branch"]
        )
        settings.github_blog_path = (
            old_values["blog_path"]
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
@router.get("/github/test")
async def test_github():
    try:
        github = GitHubClient()

        user = await github.get_current_user()
        repository = await github.get_repository()

        return {
            "success": True,
            "account": user.get("login"),
            "name": user.get("name"),
            "repository": repository.get(
                "full_name"
            ),
            "private": repository.get(
                "private"
            ),
            "branch": repository.get(
                "default_branch"
            ),
            "permissions": repository.get(
                "permissions"
            ),
        }

    except GitHubError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/github/find-blog")
async def find_blog():
    try:
        github = GitHubClient()

        paths = await github.find_blog_files()

        return {
            "success": True,
            "matches": paths,
            "count": len(paths),
        }

    except GitHubError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/github/blog")
async def read_blog():
    try:
        github = GitHubClient()

        file = await github.get_file()

        return {
            "success": True,
            "path": file.path,
            "sha": file.sha,
            "url": file.url,
            "length": len(file.content),
            "content": file.content,
        }

    except GitHubError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/ai")
async def configure_ai(
    config: AIConfigRequest,
):
    settings.ai_provider = config.provider.strip()
    settings.ai_api_key = config.api_key.strip()
    settings.ai_base_url = config.base_url.strip().rstrip("/")
    settings.ai_model = config.model.strip()

    return {
        "success": True,
        "message": "AI provider configured successfully.",
        "ai": {
            "configured": True,
            "provider": settings.ai_provider,
            "base_url": settings.ai_base_url,
            "model": settings.ai_model,
        },
    }


@router.get("/ai")
async def get_ai_settings():
    return {
        "configured": bool(
            settings.ai_api_key
            and settings.ai_base_url
            and settings.ai_model
        ),
        "provider": settings.ai_provider,
        "base_url": settings.ai_base_url,
        "model": settings.ai_model,
    }