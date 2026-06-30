from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.schemas.movie import MovieCreate, MovieUpdate


class MovieService:
    @staticmethod
    def list_movies(db: Session, *, offset: int = 0, limit: int = 50) -> list[Movie]:
        statement = (
            select(Movie)
            .order_by(Movie.popularity_score.desc(), Movie.title.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def get_movie(db: Session, movie_id: int) -> Movie | None:
        return db.get(Movie, movie_id)

    @classmethod
    def get_movie_or_404(cls, db: Session, movie_id: int) -> Movie:
        movie = cls.get_movie(db, movie_id)
        if movie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found.",
            )
        return movie

    @staticmethod
    def create_movie(db: Session, payload: MovieCreate) -> Movie:
        movie = Movie(**payload.model_dump())
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    @classmethod
    def update_movie(
        cls,
        db: Session,
        movie_id: int,
        payload: MovieUpdate,
    ) -> Movie:
        movie = cls.get_movie_or_404(db, movie_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(movie, field, value)

        db.commit()
        db.refresh(movie)
        return movie

    @classmethod
    def delete_movie(cls, db: Session, movie_id: int) -> None:
        movie = cls.get_movie_or_404(db, movie_id)
        db.delete(movie)
        db.commit()
