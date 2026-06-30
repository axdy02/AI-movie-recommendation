from pydantic import BaseModel, ConfigDict, Field

from app.schemas.movie import MovieResponse


class RecommendationItem(BaseModel):
    movie: MovieResponse
    final_score: float = Field(ge=0, le=1)
    content_score: float = Field(ge=0, le=1)
    collaborative_score: float = Field(ge=0, le=1)
    rating_score: float = Field(ge=0, le=1)
    popularity_score: float = Field(ge=0, le=1)
    freshness_score: float = Field(ge=0, le=1)
    reason: str

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: list[RecommendationItem] = Field(default_factory=list)
