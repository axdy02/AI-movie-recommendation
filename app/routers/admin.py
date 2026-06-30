from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin_user
from app.database import get_db
from app.models.user import User
from app.schemas.movie import MovieCreate, MovieResponse, MovieUpdate
from app.services.movies import MovieService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/movies",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_movie(
    payload: MovieCreate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin_user),
) -> MovieResponse:
    movie = MovieService.create_movie(db, payload)
    return MovieResponse.model_validate(movie)


@router.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    payload: MovieUpdate,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin_user),
) -> MovieResponse:
    movie = MovieService.update_movie(db, movie_id, payload)
    return MovieResponse.model_validate(movie)


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin_user),
) -> Response:
    MovieService.delete_movie(db, movie_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/movies", response_model=list[MovieResponse])
def list_movies(
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin_user),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[MovieResponse]:
    movies = MovieService.list_movies(db, offset=offset, limit=limit)
    return [MovieResponse.model_validate(movie) for movie in movies]


@router.get("/movies/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    _current_admin: User = Depends(get_current_admin_user),
) -> MovieResponse:
    movie = MovieService.get_movie_or_404(db, movie_id)
    return MovieResponse.model_validate(movie)
