from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    watch_history: Mapped[list["WatchHistory"]] = relationship(
        "WatchHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ratings: Mapped[list["Rating"]] = relationship(
        "Rating",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    preference: Mapped["UserPreference | None"] = relationship(
        "UserPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    recommendation_logs: Mapped[list["RecommendationLog"]] = relationship(
        "RecommendationLog",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
