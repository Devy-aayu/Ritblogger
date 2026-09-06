from dataclasses import dataclass

from app.github.client import GitHubClient, GitHubError
from app.ai.parser import BlogStructure, inspect_blog_file


@dataclass
class BlogSnapshot:
    path: str
    sha: str
    content: str
    structure: BlogStructure


class BlogReader:
    async def read(self) -> BlogSnapshot:
        file = await GitHubClient().get_file()
        try:
            structure = inspect_blog_file(file.content)
        except ValueError as exc:
            raise GitHubError(
                f"Could not inspect the configured blog file: {exc}"
            ) from exc

        return BlogSnapshot(
            path=file.path,
            sha=file.sha,
            content=file.content,
            structure=structure,
        )
