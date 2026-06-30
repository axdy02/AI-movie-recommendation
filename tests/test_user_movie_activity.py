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
from app.models.watch_history import WatchHistory


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
        user = User(
            email="user@example.com",
            hashed_password="hashed",
            role="user",
            is_active=True,
        )
        session.add(user)
        session.flush()
        movies = [
            Movie(
                title="The Matrix",
                description="A hacker discovers a simulated reality.",
                genres=["action", "sci fi"],
                tags=["classic", "mind bending"],
                poster_url="https://example.com/matrix.jpg",
                rating=4.8,
                release_year=1999,
                language="english",
                cast=["Keanu Reeves", "Carrie-Anne Moss"],
                duration=8160,
                popularity_score=99.5,
            ),
            Movie(
                title="Inception",
                description="A thief enters dreams to steal secrets.",
                genres=["sci fi", "thriller"],
                tags=["dreams", "mind bending"],
                poster_url="https://example.com/inception.jpg",
                rating=4.7,
                release_year=2010,
                language="english",
                cast=["Leonardo DiCaprio"],
                duration=8880,
                popularity_score=98.0,
            ),
        ]
        session.add_all(movies)
        session.commit()
        session.refresh(user)
        for movie in movies:
            session.refresh(movie)

        session.info["user_id"] = user.id
        session.info["movie_ids"] = [movie.id for movie in movies]
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(
            bind=engine,
            tables=[
                Rating.__table__,
                WatchHistory.__table__,
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
    token = create_access_token(subject=str(db_session.info["user_id"]))
    return {"Authorization": f"Bearer {token}"}


def test_user_can_browse_and_view_movies(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    list_response = client.get("/api/v1/movies", headers=user_headers)
    first_movie_id = list_response.json()[0]["id"]
    detail_response = client.get(
        f"/api/v1/movies/{first_movie_id}",
        headers=user_headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == first_movie_id


def test_user_can_search_movies(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    title_response = client.get(
        "/api/v1/movies/search",
        params={"q": "matrix"},
        headers=user_headers,
    )
    tag_response = client.get(
        "/api/v1/movies/search",
        params={"q": "dreams"},
        headers=user_headers,
    )

    assert title_response.status_code == 200
    assert [movie["title"] for movie in title_response.json()] == ["The Matrix"]
    assert tag_response.status_code == 200
    assert [movie["title"] for movie in tag_response.json()] == ["Inception"]


def test_user_can_filter_movies_by_genre(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/movies/genre/action", headers=user_headers)

    assert response.status_code == 200
    assert [movie["title"] for movie in response.json()] == ["The Matrix"]


def test_movie_browsing_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/movies/search", params={"q": "matrix"})

    assert response.status_code == 401


def test_user_can_record_and_list_watch_history(
    client: TestClient,
    db_session: Session,
    user_headers: dict[str, str],
) -> None:
    movie_id = db_session.info["movie_ids"][0]
    create_response = client.post(
        "/api/v1/watch-history",
        json={
            "movie_id": movie_id,
            "watch_duration_seconds": 3600,
            "completion_percentage": 44.1,
        },
        headers=user_headers,
    )
    list_response = client.get("/api/v1/watch-history/me", headers=user_headers)

    assert create_response.status_code == 201
    body = create_response.json()
    assert body["movie_id"] == movie_id
    assert body["user_id"] == db_session.info["user_id"]
    assert body["watch_duration_seconds"] == 3600
    assert body["completion_percentage"] == 44.1
    assert body["watched_at"] is not None
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_watch_history_rejects_missing_movie(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/watch-history",
        json={
            "movie_id": 999999,
            "watch_duration_seconds": 10,
            "completion_percentage": 1,
        },
        headers=user_headers,
    )

    assert response.status_code == 404


def test_user_can_create_update_and_list_ratings(
    client: TestClient,
    db_session: Session,
    user_headers: dict[str, str],
) -> None:
    movie_id = db_session.info["movie_ids"][0]
    first_response = client.post(
        "/api/v1/ratings",
        json={"movie_id": movie_id, "value": 4.5, "status": "liked"},
        headers=user_headers,
    )
    second_response = client.post(
        "/api/v1/ratings",
        json={"movie_id": movie_id, "value": 2.0, "status": "disliked"},
        headers=user_headers,
    )
    list_response = client.get("/api/v1/ratings/me", headers=user_headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json()["id"] == first_response.json()["id"]
    assert second_response.json()["value"] == 2.0
    assert second_response.json()["status"] == "disliked"
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["value"] == 2.0


def test_ratings_validate_value_and_status(
    client: TestClient,
    db_session: Session,
    user_headers: dict[str, str],
) -> None:
    movie_id = db_session.info["movie_ids"][0]
    response = client.post(
        "/api/v1/ratings",
        json={"movie_id": movie_id, "value": 6, "status": "maybe"},
        headers=user_headers,
    )

    assert response.status_code == 422
