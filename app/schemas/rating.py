from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RatingBase(BaseModel):
    movie_id: int
    rating: float = Field(ge=0, le=5)


class RatingCreate(RatingBase):
    pass


class RatingRead(RatingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
