from pydantic import BaseModel, Field


class AISettingsRequest(BaseModel):
    provider: str = "gemini"
    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None
    min_interval_hours: int = Field(default=5, ge=1, le=168)
    max_interval_hours: int = Field(default=10, ge=1, le=168)
    max_posts_per_day: int = Field(default=4, ge=1, le=20)
    enabled: bool = False
