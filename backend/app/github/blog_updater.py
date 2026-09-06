from app.github.client import GitHubClient, GitHubError
from app.github.blog_formatter import build_blog_object, insert_blog_object
from app.github.blog_reader import BlogSnapshot
from app.ai.parser import inspect_blog_file


class BlogUpdater:
    async def publish(self, snapshot: BlogSnapshot, article: dict) -> dict:
        updated = insert_blog_object(
            snapshot,
            build_blog_object(snapshot, article),
        )

        # Defensive checks: the original file must remain intact around the array
        # and the generated object must contain the exact new title and slug.
        if article["title"] not in updated or article["slug"] not in updated:
            raise GitHubError("Generated article was not inserted into the file.")
        if len(updated) <= len(snapshot.content):
            raise GitHubError("Generated file is not larger than the original file.")

        try:
            inspect_blog_file(updated)
        except Exception as exc:
            raise GitHubError(
                f"Generated blog.js failed structural validation: {exc}"
            ) from exc

        client = GitHubClient()
        return await client.update_file(
            path=snapshot.path,
            content=updated,
            sha=snapshot.sha,
            message=f"Publish article: {article['title']}",
        )
