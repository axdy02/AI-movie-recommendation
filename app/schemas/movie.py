from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MovieBase(BaseModel):
    title: str
    description: str | None = None
    genres: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    poster_url: str | None = None
    rating: float = Field(default=0.0, ge=0, le=5)
    release_year: int | None = None
    language: str | None = None
    cast: list[str] = Field(default_factory=list)
    duration: int | None = Field(default=None, ge=0)
    popularity_score: float = Field(default=0.0, ge=0)


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    genres: list[str] | None = None
    tags: list[str] | None = None
    poster_url: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    release_year: int | None = None
    language: str | None = None
    cast: list[str] | None = None
    duration: int | None = Field(default=None, ge=0)
    popularity_score: float | None = Field(default=None, ge=0)


class MovieResponse(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


MovieRead = MovieResponse
