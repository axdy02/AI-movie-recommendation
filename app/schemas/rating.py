from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RatingBase(BaseModel):
    movie_id: int
    value: float = Field(ge=0, le=5)
    status: Literal["liked", "disliked"] | None = None


class RatingCreate(RatingBase):
    pass


class RatingUpdate(BaseModel):
    value: float | None = Field(default=None, ge=0, le=5)
    status: Literal["liked", "disliked"] | None = None


class RatingResponse(RatingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


RatingRead = RatingResponse
