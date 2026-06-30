from app.models.movie import Movie
from app.models.rating import Rating
from app.models.recommendation_log import RecommendationLog
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.watch_history import WatchHistory

__all__ = [
    "Movie",
    "Rating",
    "RecommendationLog",
    "User",
    "UserPreference",
    "WatchHistory",
]
