from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import math
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user_preference import UserPreference
from app.models.watch_history import WatchHistory
from app.schemas.movie import MovieResponse
from app.schemas.recommendation import RecommendationItem
from app.services.movies import MovieService
from app.services.ollama_service import OllamaService


HYBRID_WEIGHTS = {
    "content": 0.45,
    "collaborative": 0.30,
    "rating": 0.10,
    "popularity": 0.10,
    "freshness": 0.05,
}

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class RecommendationScores:
    content: float = 0.0
    collaborative: float = 0.0
    rating: float = 0.0
    popularity: float = 0.0
    freshness: float = 0.0

    @property
    def final(self) -> float:
        return clamp_score(
            self.content * HYBRID_WEIGHTS["content"]
            + self.collaborative * HYBRID_WEIGHTS["collaborative"]
            + self.rating * HYBRID_WEIGHTS["rating"]
            + self.popularity * HYBRID_WEIGHTS["popularity"]
            + self.freshness * HYBRID_WEIGHTS["freshness"]
        )


class RecommendationService:
    @classmethod
    def recommend_for_user(
        cls,
        db: Session,
        *,
        user_id: int,
        limit: int = 10,
    ) -> list[RecommendationItem]:
        movies = cls._list_movies(db)
        watched_history = cls._list_watch_history(db, user_id=user_id)
        watched_movie_ids = {history.movie_id for history in watched_history}

        if not movies:
            return []

        if not watched_history:
            return cls._cold_start_recommendations(
                db,
                user_id=user_id,
                movies=movies,
                limit=limit,
            )

        # Content-based filtering: build TF-IDF vectors from movie metadata and
        # compare candidate movies to the user's watched movie profile.
        content_scores = cls._content_scores(
            movies=movies,
            watched_history=watched_history,
        )

        # Collaborative filtering: build user-movie interaction vectors and
        # recommend movies preferred by users similar to the current user.
        collaborative_scores = cls._collaborative_scores(
            db,
            user_id=user_id,
            watched_movie_ids=watched_movie_ids,
        )

        return cls._rank_candidates(
            movies=[
                movie for movie in movies if movie.id not in watched_movie_ids
            ],
            content_scores=content_scores,
            collaborative_scores=collaborative_scores,
            limit=limit,
            reason_builder=lambda movie, scores: cls._hybrid_reason(
                movie,
                scores,
                watched_history,
            ),
        )

    @classmethod
    def because_you_watched(
        cls,
        db: Session,
        *,
        user_id: int,
        movie_id: int,
        limit: int = 10,
    ) -> list[RecommendationItem]:
        source_movie = MovieService.get_movie_or_404(db, movie_id)
        movies = cls._list_movies(db)
        watched_movie_ids = {
            history.movie_id for history in cls._list_watch_history(db, user_id=user_id)
        }
        vectors = cls._tfidf_vectors(movies)
        source_vector = vectors.get(source_movie.id, {})

        content_scores = {
            movie.id: cosine_similarity(source_vector, vectors.get(movie.id, {}))
            for movie in movies
            if movie.id != source_movie.id
        }

        return cls._rank_candidates(
            movies=[
                movie
                for movie in movies
                if movie.id != source_movie.id and movie.id not in watched_movie_ids
            ],
            content_scores=content_scores,
            collaborative_scores={},
            limit=limit,
            reason_builder=lambda movie, scores: (
                f"Recommended because it is similar to {source_movie.title}."
            ),
        )

    @classmethod
    def similar_user_recommendations(
        cls,
        db: Session,
        *,
        user_id: int,
        limit: int = 10,
    ) -> list[RecommendationItem]:
        movies = cls._list_movies(db)
        watched_movie_ids = {
            history.movie_id for history in cls._list_watch_history(db, user_id=user_id)
        }
        collaborative_scores = cls._collaborative_scores(
            db,
            user_id=user_id,
            watched_movie_ids=watched_movie_ids,
        )

        return cls._rank_candidates(
            movies=[
                movie
                for movie in movies
                if movie.id not in watched_movie_ids
                and collaborative_scores.get(movie.id, 0.0) > 0
            ],
            content_scores={},
            collaborative_scores=collaborative_scores,
            limit=limit,
            reason_builder=lambda movie, scores: (
                "Recommended because users with similar watch and rating patterns "
                "also engaged with this movie."
            ),
        )

    @classmethod
    def trending(
        cls,
        db: Session,
        *,
        limit: int = 10,
    ) -> list[RecommendationItem]:
        movies = cls._list_movies(db)
        return cls._rank_candidates(
            movies=movies,
            content_scores={},
            collaborative_scores={},
            limit=limit,
            reason_builder=lambda movie, scores: (
                "Trending because it has strong ratings and popularity."
            ),
        )

    @classmethod
    def _cold_start_recommendations(
        cls,
        db: Session,
        *,
        user_id: int,
        movies: list[Movie],
        limit: int,
    ) -> list[RecommendationItem]:
        preference = db.scalar(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )

        if preference is None:
            return cls.trending(db, limit=limit)

        preference_scores = {
            movie.id: cls._preference_match_score(movie, preference)
            for movie in movies
        }
        matched_movies = [
            movie for movie in movies if preference_scores.get(movie.id, 0.0) > 0
        ]
        if not matched_movies:
            return cls.trending(db, limit=limit)

        return cls._rank_candidates(
            movies=matched_movies,
            content_scores=preference_scores,
            collaborative_scores={},
            limit=limit,
            reason_builder=lambda movie, scores: cls._preference_reason(
                movie,
                preference,
            ),
        )

    @classmethod
    def _rank_candidates(
        cls,
        *,
        movies: list[Movie],
        content_scores: dict[int, float],
        collaborative_scores: dict[int, float],
        limit: int,
        reason_builder,
    ) -> list[RecommendationItem]:
        if not movies:
            return []

        max_popularity = max((movie.popularity_score for movie in movies), default=0.0)
        recommendations: list[RecommendationItem] = []
        for movie in movies:
            scores = RecommendationScores(
                content=clamp_score(content_scores.get(movie.id, 0.0)),
                collaborative=clamp_score(collaborative_scores.get(movie.id, 0.0)),
                rating=clamp_score(movie.rating / 5 if movie.rating else 0.0),
                popularity=normalise_value(movie.popularity_score, max_popularity),
                freshness=cls._freshness_score(movie),
            )
            fallback_reason = reason_builder(movie, scores)
            # The deterministic recommendation score is finalized before Ollama
            # is asked for wording. Ollama can improve prose, but not ranking.
            reason = OllamaService.generate_recommendation_reason(
                movie=movie,
                fallback_reason=fallback_reason,
                signals={
                    "content_score": scores.content,
                    "collaborative_score": scores.collaborative,
                    "rating_score": scores.rating,
                    "popularity_score": scores.popularity,
                    "freshness_score": scores.freshness,
                },
            )
            recommendations.append(
                RecommendationItem(
                    movie=MovieResponse.model_validate(movie),
                    final_score=round(scores.final, 4),
                    content_score=round(scores.content, 4),
                    collaborative_score=round(scores.collaborative, 4),
                    rating_score=round(scores.rating, 4),
                    popularity_score=round(scores.popularity, 4),
                    freshness_score=round(scores.freshness, 4),
                    reason=reason,
                )
            )

        return sorted(
            recommendations,
            key=lambda item: (item.final_score, item.movie.popularity_score),
            reverse=True,
        )[:limit]

    @classmethod
    def _content_scores(
        cls,
        *,
        movies: list[Movie],
        watched_history: list[WatchHistory],
    ) -> dict[int, float]:
        vectors = cls._tfidf_vectors(movies)
        weighted_profile: dict[str, float] = defaultdict(float)
        watched_ids = {history.movie_id for history in watched_history}

        for history in watched_history:
            movie_vector = vectors.get(history.movie_id, {})
            weight = 0.5 + (history.completion_percentage / 100)
            for token, value in movie_vector.items():
                weighted_profile[token] += value * weight

        return {
            movie.id: cosine_similarity(weighted_profile, vectors.get(movie.id, {}))
            for movie in movies
            if movie.id not in watched_ids
        }

    @classmethod
    def _collaborative_scores(
        cls,
        db: Session,
        *,
        user_id: int,
        watched_movie_ids: set[int],
    ) -> dict[int, float]:
        interactions = cls._user_movie_interactions(db)
        current_vector = interactions.get(user_id, {})
        if not current_vector:
            return {}

        similar_users: list[tuple[int, float]] = []
        for other_user_id, other_vector in interactions.items():
            if other_user_id == user_id:
                continue
            similarity = cosine_similarity(current_vector, other_vector)
            if similarity > 0:
                similar_users.append((other_user_id, similarity))

        score_totals: dict[int, float] = defaultdict(float)
        similarity_totals: dict[int, float] = defaultdict(float)
        for similar_user_id, similarity in similar_users:
            for movie_id, interaction_score in interactions[similar_user_id].items():
                if movie_id in watched_movie_ids:
                    continue
                score_totals[movie_id] += similarity * interaction_score
                similarity_totals[movie_id] += similarity

        return {
            movie_id: clamp_score(score_totals[movie_id] / similarity_totals[movie_id])
            for movie_id in score_totals
            if similarity_totals[movie_id] > 0
        }

    @classmethod
    def _user_movie_interactions(cls, db: Session) -> dict[int, dict[int, float]]:
        interactions: dict[int, dict[int, float]] = defaultdict(dict)

        for history in db.scalars(select(WatchHistory)).all():
            watch_score = 0.2 + (history.completion_percentage / 100) * 0.6
            if history.watch_duration_seconds > 0:
                watch_score += 0.1
            interactions[history.user_id][history.movie_id] = max(
                interactions[history.user_id].get(history.movie_id, 0.0),
                clamp_score(watch_score),
            )

        for rating in db.scalars(select(Rating)).all():
            rating_score = rating.value / 5
            if rating.status == "liked":
                rating_score = min(1.0, rating_score + 0.2)
            elif rating.status == "disliked":
                rating_score = max(0.0, rating_score - 0.3)

            existing_score = interactions[rating.user_id].get(rating.movie_id, 0.0)
            interactions[rating.user_id][rating.movie_id] = max(
                existing_score,
                clamp_score(rating_score),
            )

        return interactions

    @staticmethod
    def _tfidf_vectors(movies: list[Movie]) -> dict[int, dict[str, float]]:
        tokenised_docs = {
            movie.id: tokenize_movie(movie)
            for movie in movies
        }
        document_count = len(tokenised_docs)
        document_frequency: Counter[str] = Counter()

        for tokens in tokenised_docs.values():
            document_frequency.update(set(tokens))

        vectors: dict[int, dict[str, float]] = {}
        for movie_id, tokens in tokenised_docs.items():
            if not tokens:
                vectors[movie_id] = {}
                continue

            token_counts = Counter(tokens)
            token_total = len(tokens)
            vector: dict[str, float] = {}
            for token, count in token_counts.items():
                tf = count / token_total
                idf = math.log((1 + document_count) / (1 + document_frequency[token])) + 1
                vector[token] = tf * idf
            vectors[movie_id] = vector

        return vectors

    @staticmethod
    def _list_movies(db: Session) -> list[Movie]:
        return list(
            db.scalars(
                select(Movie).order_by(Movie.popularity_score.desc(), Movie.title.asc())
            ).all()
        )

    @staticmethod
    def _list_watch_history(db: Session, *, user_id: int) -> list[WatchHistory]:
        return list(
            db.scalars(
                select(WatchHistory).where(WatchHistory.user_id == user_id)
            ).all()
        )

    @staticmethod
    def _freshness_score(movie: Movie) -> float:
        if movie.release_year is None:
            return 0.0
        current_year = datetime.now(timezone.utc).year
        return clamp_score((movie.release_year - 1888) / (current_year - 1888))

    @staticmethod
    def _preference_match_score(movie: Movie, preference: UserPreference) -> float:
        score = 0.0
        preferred_genres = {item.lower() for item in preference.preferred_genres}
        preferred_tags = {item.lower() for item in preference.preferred_tags}
        preferred_languages = {
            item.lower() for item in preference.preferred_languages
        }

        if preferred_genres and preferred_genres.intersection(movie.genres):
            score += 0.45
        if preferred_tags and preferred_tags.intersection(movie.tags):
            score += 0.35
        if movie.language and movie.language.lower() in preferred_languages:
            score += 0.20
        return clamp_score(score)

    @staticmethod
    def _hybrid_reason(
        movie: Movie,
        scores: RecommendationScores,
        watched_history: list[WatchHistory],
    ) -> str:
        watched_genres: Counter[str] = Counter()
        watched_tags: Counter[str] = Counter()
        for history in watched_history:
            watched_movie = history.movie
            watched_genres.update(watched_movie.genres)
            watched_tags.update(watched_movie.tags)

        genre_hint = first_overlap(movie.genres, watched_genres)
        tag_hint = first_overlap(movie.tags, watched_tags)

        if scores.collaborative >= scores.content and scores.collaborative > 0:
            return (
                "Recommended because users with similar watch and rating patterns "
                "also liked this movie."
            )
        if genre_hint and tag_hint:
            return (
                f"Recommended because you watched {genre_hint} movies with "
                f"{tag_hint} themes."
            )
        if genre_hint:
            return f"Recommended because you watched similar {genre_hint} movies."
        return "Recommended because it matches your recent watch history."

    @staticmethod
    def _preference_reason(movie: Movie, preference: UserPreference) -> str:
        for genre in movie.genres:
            if genre in preference.preferred_genres:
                return f"Recommended because you prefer {genre} movies."
        for tag in movie.tags:
            if tag in preference.preferred_tags:
                return f"Recommended because you prefer {tag} themes."
        if movie.language in preference.preferred_languages:
            return f"Recommended because you prefer {movie.language} movies."
        return "Recommended because it matches your saved preferences."


def tokenize_movie(movie: Movie) -> list[str]:
    metadata = [
        movie.title,
        movie.description or "",
        movie.language or "",
        " ".join(movie.genres),
        " ".join(movie.tags),
        " ".join(movie.cast),
    ]
    return TOKEN_PATTERN.findall(" ".join(metadata).lower())


def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0

    shared_tokens = set(left).intersection(right)
    dot_product = sum(left[token] * right[token] for token in shared_tokens)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return clamp_score(dot_product / (left_norm * right_norm))


def clamp_score(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return max(0.0, min(1.0, value))


def normalise_value(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0.0
    return clamp_score(value / max_value)


def first_overlap(items: list[str], weighted_items: Counter[str]) -> str | None:
    ranked_items = [item for item, _count in weighted_items.most_common()]
    for item in ranked_items:
        if item in items:
            return item
    return None
