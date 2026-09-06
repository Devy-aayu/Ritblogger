
from app.ai.parser import inspect_blog_file
from app.github.blog_reader import BlogSnapshot
from app.github.blog_formatter import build_blog_object, insert_blog_object


def test_insert_preserves_valid_array():
    source = """export const blogs = [
  {
    id: 1,
    title: "Old title",
    slug: "old-title",
    excerpt: "Old excerpt",
    content: "<p>Hello</p>",
    category: "Technology",
    tags: ["ai"],
    author: "Ritnav",
    date: "2026-08-01",
    readTime: 4,
  },
];
"""
    structure = inspect_blog_file(source)
    snapshot = BlogSnapshot("blogs.js", "sha", source, structure)

    article = {
        "title": "New AI Story",
        "slug": "new-ai-story",
        "excerpt": "A useful explanation of a new AI development.",
        "content": "<h2>What changed?</h2><p>" + ("Useful detail. " * 120) + "</p>",
        "category": "Technology",
        "tags": ["ai", "technology"],
        "seo_title": "New AI Story",
        "meta_description": "A useful explanation of a new AI development and why it matters.",
        "primary_keyword": "new AI story",
        "secondary_keywords": ["AI news"],
        "faq": [{"question": "What changed?", "answer": "A new development occurred."}],
        "read_time": 5,
    }

    obj = build_blog_object(snapshot, article)
    updated = insert_blog_object(snapshot, obj)
    updated_structure = inspect_blog_file(updated)

    assert "New AI Story" in updated
    assert "new-ai-story" in updated
    assert updated_structure.fields == structure.fields
