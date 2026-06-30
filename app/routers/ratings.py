from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingResponse
from app.services.ratings import RatingService

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_rating(
    payload: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RatingResponse:
    rating = RatingService.create_or_update_rating(
        db,
        user_id=current_user.id,
        payload=payload,
    )
    return RatingResponse.model_validate(rating)


@router.get("/me", response_model=list[RatingResponse])
def list_my_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[RatingResponse]:
    ratings = RatingService.list_for_user(
        db,
        user_id=current_user.id,
        offset=offset,
        limit=limit,
    )
    return [RatingResponse.model_validate(rating) for rating in ratings]
