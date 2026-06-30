from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WatchHistoryCreate(BaseModel):
    movie_id: int
    watched_at: datetime | None = None


class WatchHistoryRead(BaseModel):
    id: int
    user_id: int
    movie_id: int
    watched_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
