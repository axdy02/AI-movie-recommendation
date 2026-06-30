from pydantic import BaseModel, Field

from app.schemas.movie import MovieResponse


class RecommendationResponse(BaseModel):
    user_id: int
    movies: list[MovieResponse] = Field(default_factory=list)
