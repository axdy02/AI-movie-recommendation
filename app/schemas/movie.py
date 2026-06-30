from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MovieBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    genres: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    poster_url: str | None = Field(default=None, max_length=500)
    rating: float = Field(default=0.0, ge=0, le=5)
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    language: str | None = Field(default=None, max_length=50)
    cast: list[str] = Field(default_factory=list)
    duration: int | None = Field(default=None, ge=0)
    popularity_score: float = Field(default=0.0, ge=0)

    @field_validator("title", mode="before")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Value must be a string.")
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("Value cannot be empty.")
        return cleaned

    @field_validator("description", "poster_url", "language", mode="before")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None

    @field_validator("poster_url")
    @classmethod
    def validate_poster_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("Poster URL must start with http:// or https://.")
        return value

    @field_validator("language")
    @classmethod
    def clean_language(cls, value: str | None) -> str | None:
        return value.lower() if value else None

    @field_validator("genres", "tags", mode="before")
    @classmethod
    def clean_keyword_list(cls, value: Any) -> list[str]:
        return clean_string_list(value, lowercase=True)

    @field_validator("cast", mode="before")
    @classmethod
    def clean_cast_list(cls, value: Any) -> list[str]:
        return clean_string_list(value, lowercase=False)


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    genres: list[str] | None = None
    tags: list[str] | None = None
    poster_url: str | None = Field(default=None, max_length=500)
    rating: float | None = Field(default=None, ge=0, le=5)
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    language: str | None = Field(default=None, max_length=50)
    cast: list[str] | None = None
    duration: int | None = Field(default=None, ge=0)
    popularity_score: float | None = Field(default=None, ge=0)

    @field_validator("title", mode="before")
    @classmethod
    def clean_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Value must be a string.")
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            raise ValueError("Value cannot be empty.")
        return cleaned

    @field_validator("description", "poster_url", "language", mode="before")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None

    @field_validator("poster_url")
    @classmethod
    def validate_poster_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("Poster URL must start with http:// or https://.")
        return value

    @field_validator("language")
    @classmethod
    def clean_language(cls, value: str | None) -> str | None:
        return value.lower() if value else None

    @field_validator("genres", "tags", mode="before")
    @classmethod
    def clean_keyword_list(cls, value: Any) -> list[str] | None:
        if value is None:
            return None
        return clean_string_list(value, lowercase=True)

    @field_validator("cast", mode="before")
    @classmethod
    def clean_cast_list(cls, value: Any) -> list[str] | None:
        if value is None:
            return None
        return clean_string_list(value, lowercase=False)


class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


MovieRead = MovieResponse


def clean_string_list(value: Any, *, lowercase: bool) -> list[str]:
    if value is None:
        return []

    raw_items = value.split(",") if isinstance(value, str) else value
    if not isinstance(raw_items, list):
        raise ValueError("Value must be a list of strings.")

    cleaned_items: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        if not isinstance(item, str):
            raise ValueError("Every item must be a string.")

        cleaned = " ".join(item.strip().split())
        if not cleaned:
            continue

        normalized = cleaned.lower() if lowercase else cleaned
        dedupe_key = normalized.lower()
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        cleaned_items.append(normalized)

    return cleaned_items
