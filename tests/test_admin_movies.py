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
from app.models.user import User


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=[User.__table__, Movie.__table__])
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = testing_session_local()

    try:
        admin = User(
            email="admin@example.com",
            hashed_password="hashed",
            role="admin",
            is_active=True,
        )
        user = User(
            email="user@example.com",
            hashed_password="hashed",
            role="user",
            is_active=True,
        )
        session.add_all([admin, user])
        session.commit()
        session.refresh(admin)
        session.refresh(user)
        session.info["admin_id"] = admin.id
        session.info["user_id"] = user.id
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine, tables=[Movie.__table__, User.__table__])


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(db_session: Session) -> dict[str, str]:
    token = create_access_token(subject=str(db_session.info["admin_id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_headers(db_session: Session) -> dict[str, str]:
    token = create_access_token(subject=str(db_session.info["user_id"]))
    return {"Authorization": f"Bearer {token}"}


def movie_payload() -> dict[str, object]:
    return {
        "title": "  The Matrix  ",
        "description": "  A hacker discovers reality is not what it seems.  ",
        "genres": [" Action ", "action", "", " Sci Fi "],
        "tags": "Classic, Mind Bending, classic",
        "poster_url": "https://example.com/poster.jpg",
        "rating": 4.8,
        "release_year": 1999,
        "language": " English ",
        "cast": [" Keanu Reeves ", "keanu reeves", "Carrie-Anne Moss"],
        "duration": 8160,
        "popularity_score": 99.5,
    }


def test_admin_can_create_movie_with_clean_list_fields(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/admin/movies",
        json=movie_payload(),
        headers=admin_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "The Matrix"
    assert body["genres"] == ["action", "sci fi"]
    assert body["tags"] == ["classic", "mind bending"]
    assert body["cast"] == ["Keanu Reeves", "Carrie-Anne Moss"]
    assert body["language"] == "english"


def test_normal_user_cannot_create_or_list_admin_movies(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/admin/movies",
        json=movie_payload(),
        headers=user_headers,
    )
    list_response = client.get("/api/v1/admin/movies", headers=user_headers)

    assert create_response.status_code == 403
    assert list_response.status_code == 403


def test_protected_public_movie_routes_allow_normal_user(
    client: TestClient,
    admin_headers: dict[str, str],
    user_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/admin/movies",
        json=movie_payload(),
        headers=admin_headers,
    )
    movie_id = create_response.json()["id"]

    list_response = client.get("/api/v1/movies", headers=user_headers)
    detail_response = client.get(f"/api/v1/movies/{movie_id}", headers=user_headers)

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == movie_id


def test_public_movie_routes_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/movies")

    assert response.status_code == 401


def test_admin_can_update_and_delete_movie(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/api/v1/admin/movies",
        json=movie_payload(),
        headers=admin_headers,
    )
    movie_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/admin/movies/{movie_id}",
        json={
            "title": "  The Matrix Reloaded  ",
            "genres": "Action, Sequel, action",
            "rating": 4.1,
        },
        headers=admin_headers,
    )
    delete_response = client.delete(
        f"/api/v1/admin/movies/{movie_id}",
        headers=admin_headers,
    )
    missing_response = client.get(
        f"/api/v1/admin/movies/{movie_id}",
        headers=admin_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "The Matrix Reloaded"
    assert update_response.json()["genres"] == ["action", "sequel"]
    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


def test_movie_field_validation(client: TestClient, admin_headers: dict[str, str]) -> None:
    invalid_payload = movie_payload()
    invalid_payload["title"] = "   "
    invalid_payload["poster_url"] = "not-a-url"
    invalid_payload["rating"] = 8

    response = client.post(
        "/api/v1/admin/movies",
        json=invalid_payload,
        headers=admin_headers,
    )

    assert response.status_code == 422
