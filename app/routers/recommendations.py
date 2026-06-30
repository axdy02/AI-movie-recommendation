from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationItem
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/me", response_model=list[RecommendationItem])
def get_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[RecommendationItem]:
    return RecommendationService.recommend_for_user(
        db,
        user_id=current_user.id,
        limit=limit,
    )


@router.get("/because-you-watched/{movie_id}", response_model=list[RecommendationItem])
def get_recommendations_because_you_watched(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[RecommendationItem]:
    return RecommendationService.because_you_watched(
        db,
        user_id=current_user.id,
        movie_id=movie_id,
        limit=limit,
    )


@router.get("/similar-users", response_model=list[RecommendationItem])
def get_similar_user_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[RecommendationItem]:
    return RecommendationService.similar_user_recommendations(
        db,
        user_id=current_user.id,
        limit=limit,
    )


@router.get("/trending", response_model=list[RecommendationItem])
def get_trending_recommendations(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[RecommendationItem]:
    return RecommendationService.trending(db, limit=limit)
