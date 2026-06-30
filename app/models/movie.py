from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

json_list_type = JSON().with_variant(JSONB, "postgresql")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_movies_rating_range"),
        CheckConstraint(
            "duration IS NULL OR duration >= 0",
            name="ck_movies_duration_nonnegative",
        ),
        CheckConstraint(
            "popularity_score >= 0",
            name="ck_movies_popularity_score_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genres: Mapped[list[str]] = mapped_column(json_list_type, default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(json_list_type, default=list, nullable=False)
    poster_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    release_year: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    cast: Mapped[list[str]] = mapped_column(json_list_type, default=list, nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    popularity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    watch_history: Mapped[list["WatchHistory"]] = relationship(
        "WatchHistory",
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ratings: Mapped[list["Rating"]] = relationship(
        "Rating",
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    recommendation_logs: Mapped[list["RecommendationLog"]] = relationship(
        "RecommendationLog",
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
