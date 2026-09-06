import base64
from dataclasses import dataclass

import httpx

from app.core.config import settings


GITHUB_API = "https://api.github.com"


class GitHubError(Exception):
    pass


@dataclass
class GitHubFile:
    path: str
    content: str
    sha: str
    url: str


class GitHubClient:
    def __init__(self):
        if not settings.github_token:
            raise GitHubError("GITHUB_TOKEN is empty.")

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": "2026-03-10",
        }

    async def get_current_user(self):
        url = f"{GITHUB_API}/user"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                url,
                headers=self.headers,
            )

        if response.status_code != 200:
            raise GitHubError(
                f"Token authentication failed. "
                f"GitHub returned {response.status_code}: "
                f"{response.text}"
            )

        return response.json()

    async def get_repository(self):
        if not settings.github_owner:
            raise GitHubError("GITHUB_OWNER is empty.")

        if not settings.github_repository:
            raise GitHubError(
                "GITHUB_REPOSITORY is empty."
            )

        url = (
            f"{GITHUB_API}/repos/"
            f"{settings.github_owner}/"
            f"{settings.github_repository}"
        )

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                url,
                headers=self.headers,
            )

        if response.status_code != 200:
            raise GitHubError(
                f"Repository request failed. "
                f"GitHub returned {response.status_code}: "
                f"{response.text}"
            )

        return response.json()

    async def get_file(self):
        if not settings.github_blog_path:
            raise GitHubError(
                "GITHUB_BLOG_PATH is empty."
            )

        url = (
            f"{GITHUB_API}/repos/"
            f"{settings.github_owner}/"
            f"{settings.github_repository}/"
            f"contents/"
            f"{settings.github_blog_path}"
        )

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                url,
                headers=self.headers,
                params={
                    "ref": settings.github_branch,
                },
            )

        if response.status_code != 200:
            raise GitHubError(
                f"File request failed. "
                f"GitHub returned {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        if data.get("type") != "file":
            raise GitHubError(
                "The configured blog path is not a file."
            )

        encoded_content = data.get(
            "content",
            "",
        ).replace("\n", "")

        try:
            content = base64.b64decode(
                encoded_content
            ).decode("utf-8")
        except Exception as exc:
            raise GitHubError(
                f"Could not decode GitHub file: {exc}"
            ) from exc

        return GitHubFile(
            path=data["path"],
            content=content,
            sha=data["sha"],
            url=data.get("html_url", ""),
        )