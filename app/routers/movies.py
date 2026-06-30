from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.movie import MovieResponse
from app.services.movies import MovieService

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=list[MovieResponse])
def list_movies(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[MovieResponse]:
    movies = MovieService.list_movies(db, offset=offset, limit=limit)
    return [MovieResponse.model_validate(movie) for movie in movies]


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> MovieResponse:
    movie = MovieService.get_movie_or_404(db, movie_id)
    return MovieResponse.model_validate(movie)
