import json
import re
from typing import Any


class BlogFormatError(Exception):
    pass


class BlogFormatter:
    def analyze_structure(
        self,
        blog_source: str,
    ) -> dict[str, Any]:
        top_level_keys = []

        for match in re.finditer(
            r"^\s{4}([A-Za-z_$][\w$]*)\s*:",
            blog_source,
            flags=re.MULTILINE,
        ):
            key = match.group(1)

            if key not in top_level_keys:
                top_level_keys.append(key)

        content_types = []

        for match in re.finditer(
            r"type\s*:\s*[\"']([^\"']+)",
            blog_source,
        ):
            value = match.group(1)

            if value not in content_types:
                content_types.append(value)

        titles = re.findall(
            r"^\s*title\s*:\s*[\"']([^\"']+)",
            blog_source,
            flags=re.MULTILINE,
        )

        categories = re.findall(
            r"^\s*category\s*:\s*[\"']([^\"']+)",
            blog_source,
            flags=re.MULTILINE,
        )

        sample = blog_source[:20000]

        return {
            "top_level_keys": top_level_keys,
            "content_types": content_types,
            "sample_titles": titles[:10],
            "sample_categories": categories[:20],
            "sample_source": sample,
        }

    def build_blog_object(
        self,
        generated: dict[str, Any],
        structure: dict[str, Any],
    ) -> dict[str, Any]:
        allowed_keys = set(
            structure.get(
                "top_level_keys",
                [],
            )
        )

        if not allowed_keys:
            raise BlogFormatError(
                "Could not determine blog.js structure."
            )

        article = {}

        for key in allowed_keys:
            if key in generated:
                article[key] = generated[key]

        required = [
            "slug",
            "title",
            "description",
            "category",
            "date",
            "author",
            "readTime",
            "content",
        ]

        missing = [
            key
            for key in required
            if key in allowed_keys
            and key not in article
        ]

        if missing:
            raise BlogFormatError(
                "Generated article is missing: "
                + ", ".join(missing)
            )

        allowed_types = set(
            structure.get(
                "content_types",
                [],
            )
        )

        content = article.get("content")

        if isinstance(content, list):
            if allowed_types:
                for block in content:
                    if not isinstance(
                        block,
                        dict,
                    ):
                        raise BlogFormatError(
                            "Invalid content block."
                        )

                    block_type = block.get("type")

                    if (
                        block_type
                        and block_type
                        not in allowed_types
                    ):
                        raise BlogFormatError(
                            "Unsupported content "
                            f"type: {block_type}"
                        )

        return article

    def insert_article(
        self,
        blog_source: str,
        article: dict[str, Any],
    ) -> str:
        marker = "export const blogs = ["

        position = blog_source.find(
            marker
        )

        if position == -1:
            raise BlogFormatError(
                "Could not find "
                "'export const blogs = ['."
            )

        insert_position = (
            position + len(marker)
        )

        serialized = json.dumps(
            article,
            ensure_ascii=False,
            indent=2,
        )

        insertion = (
            "\n  "
            + serialized.replace(
                "\n",
                "\n  ",
            )
            + ",\n"
        )

        return (
            blog_source[:insert_position]
            + insertion
            + blog_source[insert_position:]
        )