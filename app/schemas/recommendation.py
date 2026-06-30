from pydantic import BaseModel, Field

from app.schemas.movie import MovieRead


class RecommendationResponse(BaseModel):
    user_id: int
    movies: list[MovieRead] = Field(default_factory=list)
