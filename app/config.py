from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Movie Recommendation API"
    api_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    environment: str = "local"
    debug: bool = False

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/ai_movie_recommendation"
    )

    secret_key: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

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
