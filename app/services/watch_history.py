from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.watch_history import WatchHistory
from app.schemas.watch_history import WatchHistoryCreate
from app.services.movies import MovieService


class WatchHistoryService:
    @staticmethod
    def record_watch(
        db: Session,
        *,
        user_id: int,
        payload: WatchHistoryCreate,
    ) -> WatchHistory:
        MovieService.get_movie_or_404(db, payload.movie_id)
        watch_history = WatchHistory(
            user_id=user_id,
            movie_id=payload.movie_id,
            watched_at=payload.watched_at or datetime.now(timezone.utc),
            watch_duration_seconds=payload.watch_duration_seconds,
            completion_percentage=payload.completion_percentage,
        )
        db.add(watch_history)
        db.commit()
        db.refresh(watch_history)
        return watch_history

    @staticmethod
    def list_for_user(
        db: Session,
        *,
        user_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> list[WatchHistory]:
        statement = (
            select(WatchHistory)
            .where(WatchHistory.user_id == user_id)
            .order_by(WatchHistory.watched_at.desc(), WatchHistory.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(statement).all())
