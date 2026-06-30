from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rating import Rating
from app.schemas.rating import RatingCreate
from app.services.movies import MovieService


class RatingService:
    @staticmethod
    def create_or_update_rating(
        db: Session,
        *,
        user_id: int,
        payload: RatingCreate,
    ) -> Rating:
        MovieService.get_movie_or_404(db, payload.movie_id)
        statement = select(Rating).where(
            Rating.user_id == user_id,
            Rating.movie_id == payload.movie_id,
        )
        rating = db.scalar(statement)

        if rating is None:
            rating = Rating(
                user_id=user_id,
                movie_id=payload.movie_id,
                value=payload.value,
                status=payload.status,
            )
            db.add(rating)
        else:
            rating.value = payload.value
            rating.status = payload.status

        db.commit()
        db.refresh(rating)
        return rating

    @staticmethod
    def list_for_user(
        db: Session,
        *,
        user_id: int,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Rating]:
        statement = (
            select(Rating)
            .where(Rating.user_id == user_id)
            .order_by(Rating.updated_at.desc(), Rating.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(statement).all())
