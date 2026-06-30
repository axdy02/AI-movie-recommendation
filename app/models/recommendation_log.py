from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"
    __table_args__ = (
        CheckConstraint(
            "recommendation_score IS NULL OR recommendation_score >= 0",
            name="ck_recommendation_logs_score_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"),
        index=True,
    )
    recommendation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    algorithm_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="recommendation_logs")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="recommendation_logs")
