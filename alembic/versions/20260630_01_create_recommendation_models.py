"""create recommendation backend models

Revision ID: 20260630_01
Revises:
Create Date: 2026-06-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260630_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column(
            "role",
            sa.String(length=20),
            server_default=sa.text("'user'"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("role IN ('user', 'admin')", name="ck_users_role"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "movies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "genres",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("poster_url", sa.String(length=500), nullable=True),
        sa.Column("rating", sa.Float(), server_default=sa.text("0"), nullable=False),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column(
            "cast",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column(
            "popularity_score",
            sa.Float(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="ck_movies_rating_range"),
        sa.CheckConstraint(
            "duration IS NULL OR duration >= 0",
            name="ck_movies_duration_nonnegative",
        ),
        sa.CheckConstraint(
            "popularity_score >= 0",
            name="ck_movies_popularity_score_nonnegative",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_movies_language"), "movies", ["language"], unique=False)
    op.create_index(op.f("ix_movies_release_year"), "movies", ["release_year"], unique=False)
    op.create_index(op.f("ix_movies_title"), "movies", ["title"], unique=False)

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "preferred_genres",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "preferred_tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "preferred_languages",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "watch_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column(
            "watched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "watch_duration_seconds",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "completion_percentage",
            sa.Float(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "completion_percentage >= 0 AND completion_percentage <= 100",
            name="ck_watch_history_completion_percentage",
        ),
        sa.CheckConstraint(
            "watch_duration_seconds >= 0",
            name="ck_watch_history_duration_nonnegative",
        ),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_watch_history_movie_id"),
        "watch_history",
        ["movie_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watch_history_user_id"),
        "watch_history",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_watch_history_watched_at"),
        "watch_history",
        ["watched_at"],
        unique=False,
    )

    op.create_table(
        "ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IS NULL OR status IN ('liked', 'disliked')",
            name="ck_ratings_status",
        ),
        sa.CheckConstraint("value >= 0 AND value <= 5", name="ck_ratings_value_range"),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "movie_id", name="uq_ratings_user_movie"),
    )
    op.create_index(op.f("ix_ratings_movie_id"), "ratings", ["movie_id"], unique=False)
    op.create_index(op.f("ix_ratings_user_id"), "ratings", ["user_id"], unique=False)

    op.create_table(
        "recommendation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("recommendation_score", sa.Float(), nullable=True),
        sa.Column("algorithm_version", sa.String(length=100), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "recommendation_score IS NULL OR recommendation_score >= 0",
            name="ck_recommendation_logs_score_nonnegative",
        ),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recommendation_logs_created_at"),
        "recommendation_logs",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendation_logs_movie_id"),
        "recommendation_logs",
        ["movie_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendation_logs_user_id"),
        "recommendation_logs",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_recommendation_logs_user_id"), table_name="recommendation_logs")
    op.drop_index(op.f("ix_recommendation_logs_movie_id"), table_name="recommendation_logs")
    op.drop_index(op.f("ix_recommendation_logs_created_at"), table_name="recommendation_logs")
    op.drop_table("recommendation_logs")

    op.drop_index(op.f("ix_ratings_user_id"), table_name="ratings")
    op.drop_index(op.f("ix_ratings_movie_id"), table_name="ratings")
    op.drop_table("ratings")

    op.drop_index(op.f("ix_watch_history_watched_at"), table_name="watch_history")
    op.drop_index(op.f("ix_watch_history_user_id"), table_name="watch_history")
    op.drop_index(op.f("ix_watch_history_movie_id"), table_name="watch_history")
    op.drop_table("watch_history")

    op.drop_table("user_preferences")

    op.drop_index(op.f("ix_movies_title"), table_name="movies")
    op.drop_index(op.f("ix_movies_release_year"), table_name="movies")
    op.drop_index(op.f("ix_movies_language"), table_name="movies")
    op.drop_table("movies")

    op.drop_table("users")
