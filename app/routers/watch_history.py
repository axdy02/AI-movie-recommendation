from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.watch_history import WatchHistoryCreate, WatchHistoryResponse
from app.services.watch_history import WatchHistoryService

router = APIRouter(prefix="/watch-history", tags=["watch_history"])


@router.post(
    "",
    response_model=WatchHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_watch_history(
    payload: WatchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WatchHistoryResponse:
    watch_history = WatchHistoryService.record_watch(
        db,
        user_id=current_user.id,
        payload=payload,
    )
    return WatchHistoryResponse.model_validate(watch_history)


@router.get("/me", response_model=list[WatchHistoryResponse])
def list_my_watch_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[WatchHistoryResponse]:
    watch_history = WatchHistoryService.list_for_user(
        db,
        user_id=current_user.id,
        offset=offset,
        limit=limit,
    )
    return [WatchHistoryResponse.model_validate(item) for item in watch_history]
