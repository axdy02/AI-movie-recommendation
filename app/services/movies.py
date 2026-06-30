from fastapi import HTTPException, status
from sqlalchemy import or_, select
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
    def search_movies(
        db: Session,
        *,
        query: str,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Movie]:
        clean_query = query.strip().lower()
        if not clean_query:
            return []

        text_pattern = f"%{clean_query}%"
        statement = (
            select(Movie)
            .where(
                or_(
                    Movie.title.ilike(text_pattern),
                    Movie.description.ilike(text_pattern),
                    Movie.language.ilike(text_pattern),
                )
            )
            .order_by(Movie.popularity_score.desc(), Movie.title.asc())
        )
        text_matches = list(db.scalars(statement).all())

        json_matches = [
            movie
            for movie in MovieService._list_all_movies(db)
            if MovieService._movie_has_list_match(movie, clean_query)
        ]

        return MovieService._merge_movies(text_matches, json_matches)[offset : offset + limit]

    @staticmethod
    def list_movies_by_genre(
        db: Session,
        *,
        genre: str,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Movie]:
        clean_genre = " ".join(genre.strip().lower().split())
        if not clean_genre:
            return []

        matches = [
            movie
            for movie in MovieService._list_all_movies(db)
            if any(clean_genre == genre.lower() for genre in movie.genres)
        ]
        return matches[offset : offset + limit]

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

    @staticmethod
    def _movie_has_list_match(movie: Movie, query: str) -> bool:
        list_fields = (*movie.genres, *movie.tags, *movie.cast)
        return any(query in item.lower() for item in list_fields)

    @staticmethod
    def _list_all_movies(db: Session) -> list[Movie]:
        statement = select(Movie).order_by(Movie.popularity_score.desc(), Movie.title.asc())
        return list(db.scalars(statement).all())

    @staticmethod
    def _merge_movies(*movie_groups: list[Movie]) -> list[Movie]:
        movies_by_id: dict[int, Movie] = {}
        for group in movie_groups:
            for movie in group:
                movies_by_id[movie.id] = movie
        return sorted(
            movies_by_id.values(),
            key=lambda movie: (-movie.popularity_score, movie.title),
        )
