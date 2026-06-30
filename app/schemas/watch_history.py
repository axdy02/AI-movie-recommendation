from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WatchHistoryCreate(BaseModel):
    user_id: int
    movie_id: int
    watched_at: datetime | None = None
    watch_duration_seconds: int = Field(default=0, ge=0)
    completion_percentage: float = Field(default=0.0, ge=0, le=100)


class WatchHistoryUpdate(BaseModel):
    watched_at: datetime | None = None
    watch_duration_seconds: int | None = Field(default=None, ge=0)
    completion_percentage: float | None = Field(default=None, ge=0, le=100)


class WatchHistoryResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    watched_at: datetime
    watch_duration_seconds: int
    completion_percentage: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


WatchHistoryRead = WatchHistoryResponse
