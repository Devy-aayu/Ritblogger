import asyncio
import base64
from dataclasses import dataclass
from typing import Any

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
    def __init__(self) -> None:
        if not settings.github_token:
            raise GitHubError(
                "GitHub token is not configured."
            )

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": (
                f"Bearer {settings.github_token}"
            ),
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Ritnav-Blog-Engine",
        }

        self.timeout = httpx.Timeout(
            60.0,
            connect=30.0,
            read=60.0,
            write=60.0,
            pool=30.0,
        )

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    http2=False,
                ) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self.headers,
                        **kwargs,
                    )

                return response

            except (
                httpx.ConnectTimeout,
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.NetworkError,
            ) as exc:
                last_error = exc

                if attempt < 2:
                    await asyncio.sleep(
                        1.5 * (attempt + 1)
                    )

        raise GitHubError(
            "Could not connect to GitHub after "
            "3 attempts. "
            f"Network error: {last_error}"
        )

    @staticmethod
    def _check_response(
        response: httpx.Response,
        action: str,
    ) -> None:
        if response.status_code >= 400:
            raise GitHubError(
                f"{action} failed. "
                f"GitHub returned "
                f"{response.status_code}: "
                f"{response.text[:1000]}"
            )

    async def get_current_user(
        self,
    ) -> dict[str, Any]:
        response = await self._request(
            "GET",
            f"{GITHUB_API}/user",
        )

        self._check_response(
            response,
            "GitHub authentication",
        )

        return response.json()

    async def get_repository(
        self,
    ) -> dict[str, Any]:
        if not settings.github_owner:
            raise GitHubError(
                "GITHUB_OWNER is not configured."
            )

        if not settings.github_repository:
            raise GitHubError(
                "GITHUB_REPOSITORY is not configured."
            )

        url = (
            f"{GITHUB_API}/repos/"
            f"{settings.github_owner}/"
            f"{settings.github_repository}"
        )

        response = await self._request(
            "GET",
            url,
        )

        self._check_response(
            response,
            "GitHub repository request",
        )

        return response.json()

    async def get_repository_tree(
        self,
    ) -> dict[str, Any]:
        repository = (
            await self.get_repository()
        )

        branch = (
            settings.github_branch
            or repository.get(
                "default_branch",
                "main",
            )
        )

        url = (
            f"{GITHUB_API}/repos/"
            f"{settings.github_owner}/"
            f"{settings.github_repository}/"
            f"git/trees/{branch}"
        )

        response = await self._request(
            "GET",
            url,
            params={
                "recursive": "1",
            },
        )

        self._check_response(
            response,
            "GitHub repository tree request",
        )

        return response.json()

    async def find_blog_files(
        self,
    ) -> list[str]:
        tree = (
            await self.get_repository_tree()
        )

        matches: list[str] = []

        for item in tree.get(
            "tree",
            [],
        ):
            path = item.get(
                "path",
                "",
            )

            if item.get("type") != "blob":
                continue

            lower_path = path.lower()

            if (
                lower_path.endswith("blog.js")
                or lower_path.endswith("blogs.js")
            ):
                matches.append(path)

        return matches

    async def get_file(
        self,
        path: str | None = None,
    ) -> GitHubFile:
        file_path = (
            path or settings.github_blog_path
        )

        if not file_path:
            raise GitHubError(
                "GITHUB_BLOG_PATH is not configured."
            )

        file_path = (
            file_path.strip()
            .lstrip("/")
        )

        url = (
            f"{GITHUB_API}/repos/"
            f"{settings.github_owner}/"
            f"{settings.github_repository}/"
            f"contents/{file_path}"
        )

        response = await self._request(
            "GET",
            url,
            params={
                "ref": settings.github_branch,
            },
        )

        self._check_response(
            response,
            f"GitHub file request for '{file_path}'",
        )

        data = response.json()

        if data.get("type") != "file":
            raise GitHubError(
                f"'{file_path}' is not a file."
            )

        encoded = (
            data.get(
                "content",
                "",
            )
            .replace(
                "\n",
                "",
            )
        )

        try:
            content = (
                base64.b64decode(
                    encoded
                ).decode("utf-8")
            )
        except Exception as exc:
            raise GitHubError(
                "Could not decode GitHub file content."
            ) from exc

        return GitHubFile(
            path=data["path"],
            content=content,
            sha=data["sha"],
            url=data.get(
                "html_url",
                "",
            ),
        )

    async def update_file(
        self,
        content: str,
        sha: str,
        message: str,
        path: str | None = None,
    ) -> dict[str, Any]:
        file_path = (
            path or settings.github_blog_path
        )

        if not file_path:
            raise GitHubError(
                "GITHUB_BLOG_PATH is not configured."
            )

        encoded = base64.b64encode(
            content.encode("utf-8")
        ).decode("ascii")

        url = (
            f"{GITHUB_API}/repos/"
            f"{settings.github_owner}/"
            f"{settings.github_repository}/"
            f"contents/{file_path}"
        )

        payload = {
            "message": message,
            "content": encoded,
            "sha": sha,
            "branch": settings.github_branch,
        }

        response = await self._request(
            "PUT",
            url,
            json=payload,
        )

        self._check_response(
            response,
            "GitHub file update",
        )

        return response.json()