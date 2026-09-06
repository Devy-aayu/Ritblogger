from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

node_command: str = "node"
class Settings(BaseSettings):
    app_env: str = "development"

    database_url: str = "sqlite:///./data/blog_engine.db"

    admin_username: str = "admin"
    admin_password_hash: str = ""

    github_token: str = ""
    github_owner: str = ""
    github_repository: str = ""
    github_branch: str = "main"
    github_blog_path: str = ""

    ai_api_key: str = ""
    ai_model: str = ""

    news_api_key: str = ""

    automation_enabled: bool = False

    min_interval_hours: int = Field(
        default=5,
        ge=1,
    )

    max_interval_hours: int = Field(
        default=10,
        ge=1,
    )

    max_posts_per_day: int = Field(
        default=4,
        ge=1,
    )

    node_command: str = "node"

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()