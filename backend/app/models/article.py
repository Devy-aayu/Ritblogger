from pydantic import BaseModel, Field


class ArticleDraft(BaseModel):
    title: str = Field(min_length=5)
    slug: str = Field(min_length=3)
    excerpt: str = Field(min_length=20)
    content: str = Field(min_length=300)
    category: str
    tags: list[str]
    seo_title: str
    meta_description: str
    primary_keyword: str
    secondary_keywords: list[str]
    faq: list[dict[str, str]]
    read_time: int = Field(ge=1, le=60)
