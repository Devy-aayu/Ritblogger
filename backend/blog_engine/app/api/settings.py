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


@router.get("/")
async def get_settings():
    return {
        "github_configured": bool(
            settings.github_token
            and settings.github_owner
            and settings.github_repository
            and settings.github_blog_path
        ),
        "github_owner": settings.github_owner,
        "github_repository": settings.github_repository,
        "github_branch": settings.github_branch,
        "github_blog_path": settings.github_blog_path,
    }


@router.post("/github/connect")
async def connect_github(config: GitHubConfigRequest):
    settings.github_token = config.token.strip()
    settings.github_owner = config.owner.strip()
    settings.github_repository = config.repository.strip()
    settings.github_branch = config.branch.strip()
    settings.github_blog_path = config.blog_path.strip().lstrip("/")

    try:
        github = GitHubClient()

        user = await github.get_current_user()

        repository = await github.get_repository()

        blog = await github.get_file()

        return {
            "success": True,
            "message": "GitHub connected successfully.",

            "account": {
                "login": user.get("login"),
                "name": user.get("name"),
            },

            "repository": {
                "full_name": repository.get("full_name"),
                "private": repository.get("private"),
                "default_branch": repository.get("default_branch"),
                "url": repository.get("html_url"),
            },

            "blog": {
                "path": blog.path,
                "sha": blog.sha,
                "length": len(blog.content),
            },
        }

    except GitHubError as exc:
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
            "repository": repository.get("full_name"),
            "private": repository.get("private"),
            "branch": repository.get("default_branch"),
            "url": repository.get("html_url"),
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