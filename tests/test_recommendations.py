import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.auth.jwt import create_access_token
from app.database import Base, get_db
from app.main import app
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.watch_history import WatchHistory
from app.services.ollama_service import OllamaService


@pytest.fixture(autouse=True)
def use_rule_based_reasons(monkeypatch: pytest.MonkeyPatch) -> None:
    def fallback_reason(**kwargs: object) -> str:
        return str(kwargs["fallback_reason"])

    monkeypatch.setattr(
        OllamaService,
        "generate_recommendation_reason",
        fallback_reason,
    )


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        bind=engine,
        tables=[
            User.__table__,
            Movie.__table__,
            UserPreference.__table__,
            WatchHistory.__table__,
            Rating.__table__,
        ],
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = testing_session_local()

    try:
        current_user = User(
            email="current@example.com",
            hashed_password="hashed",
            role="user",
            is_active=True,
        )
        similar_user = User(
            email="similar@example.com",
            hashed_password="hashed",
            role="user",
            is_active=True,
        )
        cold_user = User(
            email="cold@example.com",
            hashed_password="hashed",
            role="user",
            is_active=True,
        )
        session.add_all([current_user, similar_user, cold_user])
        session.flush()

        matrix = Movie(
            title="The Matrix",
            description="A hacker discovers simulated reality and fights agents.",
            genres=["action", "sci fi"],
            tags=["mind bending", "chosen one"],
            poster_url="https://example.com/matrix.jpg",
            rating=4.8,
            release_year=1999,
            language="english",
            cast=["Keanu Reeves"],
            duration=8160,
            popularity_score=99.0,
        )
        john_wick = Movie(
            title="John Wick",
            description="An assassin returns for revenge in a criminal underworld.",
            genres=["action", "thriller"],
            tags=["crime", "revenge"],
            poster_url="https://example.com/wick.jpg",
            rating=4.4,
            release_year=2014,
            language="english",
            cast=["Keanu Reeves"],
            duration=6060,
            popularity_score=95.0,
        )
        dark_city = Movie(
            title="Dark City",
            description="A man questions memory and reality in a strange city.",
            genres=["sci fi", "thriller"],
            tags=["mind bending", "mystery"],
            poster_url="https://example.com/dark-city.jpg",
            rating=4.2,
            release_year=1998,
            language="english",
            cast=["Rufus Sewell"],
            duration=6000,
            popularity_score=75.0,
        )
        quiet_drama = Movie(
            title="Quiet Drama",
            description="A slow family story in a small town.",
            genres=["drama"],
            tags=["family"],
            poster_url="https://example.com/drama.jpg",
            rating=3.6,
            release_year=2021,
            language="english",
            cast=["Someone"],
            duration=6200,
            popularity_score=20.0,
        )
        session.add_all([matrix, john_wick, dark_city, quiet_drama])
        session.flush()

        session.add_all(
            [
                WatchHistory(
                    user_id=current_user.id,
                    movie_id=matrix.id,
                    watch_duration_seconds=7200,
                    completion_percentage=95,
                ),
                Rating(
                    user_id=current_user.id,
                    movie_id=matrix.id,
                    value=5,
                    status="liked",
                ),
                WatchHistory(
                    user_id=similar_user.id,
                    movie_id=matrix.id,
                    watch_duration_seconds=7000,
                    completion_percentage=91,
                ),
                Rating(
                    user_id=similar_user.id,
                    movie_id=dark_city.id,
                    value=4.8,
                    status="liked",
                ),
                WatchHistory(
                    user_id=similar_user.id,
                    movie_id=dark_city.id,
                    watch_duration_seconds=5000,
                    completion_percentage=88,
                ),
                UserPreference(
                    user_id=cold_user.id,
                    preferred_genres=["action"],
                    preferred_tags=["crime"],
                    preferred_languages=["english"],
                ),
            ]
        )
        session.commit()

        for item in [current_user, similar_user, cold_user, matrix]:
            session.refresh(item)

        session.info["current_user_id"] = current_user.id
        session.info["cold_user_id"] = cold_user.id
        session.info["matrix_id"] = matrix.id
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(
            bind=engine,
            tables=[
                Rating.__table__,
                WatchHistory.__table__,
                UserPreference.__table__,
                Movie.__table__,
                User.__table__,
            ],
        )


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def user_headers(db_session: Session) -> dict[str, str]:
    token = create_access_token(subject=str(db_session.info["current_user_id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def cold_user_headers(db_session: Session) -> dict[str, str]:
    token = create_access_token(subject=str(db_session.info["cold_user_id"]))
    return {"Authorization": f"Bearer {token}"}


def test_hybrid_recommendations_exclude_watched_movies(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/recommendations/me", headers=user_headers)

    assert response.status_code == 200
    titles = [item["movie"]["title"] for item in response.json()]
    assert "The Matrix" not in titles
    assert "Dark City" in titles

    first_item = response.json()[0]
    assert 0 <= first_item["final_score"] <= 1
    assert "content_score" in first_item
    assert "collaborative_score" in first_item
    assert first_item["reason"]


def test_because_you_watched_uses_content_similarity(
    client: TestClient,
    db_session: Session,
    user_headers: dict[str, str],
) -> None:
    response = client.get(
        f"/api/v1/recommendations/because-you-watched/{db_session.info['matrix_id']}",
        headers=user_headers,
    )

    assert response.status_code == 200
    titles = [item["movie"]["title"] for item in response.json()]
    assert "The Matrix" not in titles
    assert any("similar to The Matrix" in item["reason"] for item in response.json())


def test_similar_users_recommendations_use_collaborative_signal(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/recommendations/similar-users", headers=user_headers)

    assert response.status_code == 200
    assert response.json()[0]["movie"]["title"] == "Dark City"
    assert response.json()[0]["collaborative_score"] > 0


def test_trending_returns_popular_movies(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/recommendations/trending", headers=user_headers)

    assert response.status_code == 200
    assert response.json()[0]["movie"]["title"] == "The Matrix"
    assert response.json()[0]["reason"]


def test_cold_start_uses_preferences(
    client: TestClient,
    cold_user_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/recommendations/me", headers=cold_user_headers)

    assert response.status_code == 200
    titles = [item["movie"]["title"] for item in response.json()]
    assert "John Wick" in titles
    assert any("prefer" in item["reason"] for item in response.json())


def test_recommendations_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/recommendations/me")

    assert response.status_code == 401
