from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MovieBase(BaseModel):
    title: str
    overview: str | None = None
    release_year: int | None = None
    genres: list[str] | None = None


class MovieCreate(MovieBase):
    pass


class MovieRead(MovieBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
