from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecommendationLogBase(BaseModel):
    user_id: int
    movie_id: int
    recommendation_score: float | None = Field(default=None, ge=0)
    algorithm_version: str | None = None
    reason: str | None = None


class RecommendationLogCreate(RecommendationLogBase):
    pass


class RecommendationLogUpdate(BaseModel):
    recommendation_score: float | None = Field(default=None, ge=0)
    algorithm_version: str | None = None
    reason: str | None = None


class RecommendationLogResponse(RecommendationLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
