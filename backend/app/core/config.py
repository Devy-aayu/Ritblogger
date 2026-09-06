from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    ai_provider: str = ""
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_model: str = ""

    automation_enabled: bool = False

    cycle_timeout_minutes: int = Field(
        default=5,
        ge=1,
    )

    cycle_cooldown_minutes: int = Field(
        default=10,
        ge=1,
    )

    max_trend_results_per_country: int = Field(
        default=10,
        ge=1,
        le=50,
    )

    target_countries: str = "US,GB,CA,AU,IN"

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


def get_target_countries() -> list[str]:
    return [
        item.strip().upper()
        for item in settings.target_countries.split(",")
        if item.strip()
    ]