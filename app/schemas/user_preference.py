from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserPreferenceBase(BaseModel):
    user_id: int
    preferred_genres: list[str] = Field(default_factory=list)
    preferred_tags: list[str] = Field(default_factory=list)
    preferred_languages: list[str] = Field(default_factory=list)


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceUpdate(BaseModel):
    preferred_genres: list[str] | None = None
    preferred_tags: list[str] | None = None
    preferred_languages: list[str] | None = None


class UserPreferenceResponse(UserPreferenceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
