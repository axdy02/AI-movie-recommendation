import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.auth.dependencies import require_roles
from app.auth.passwords import verify_password
from app.database import Base, get_db
from app.main import app
from app.models.user import User


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=[User.__table__])
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine, tables=[User.__table__])


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_creates_user_with_hashed_password(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Test@Example.com",
            "password": "super-secret",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "test@example.com"
    assert body["user"]["role"] == "user"
    assert body["token"]["token_type"] == "bearer"
    assert "hashed_password" not in body["user"]

    user = db_session.scalar(select(User).where(User.email == "test@example.com"))
    assert user is not None
    assert user.hashed_password != "super-secret"
    assert verify_password("super-secret", user.hashed_password)


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "test@example.com",
        "password": "super-secret",
    }

    first_response = client.post("/api/v1/auth/register", json=payload)
    second_response = client.post("/api/v1/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_returns_token_and_me_returns_current_user(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "super-secret",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "me@example.com",
            "password": "super-secret",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "me@example.com"


def test_login_rejects_invalid_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "bad-login@example.com",
            "password": "super-secret",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "bad-login@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_me_requires_bearer_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_require_roles_allows_only_matching_roles() -> None:
    user = User(
        id=1,
        email="user@example.com",
        hashed_password="hashed",
        role="user",
    )
    admin = User(
        id=2,
        email="admin@example.com",
        hashed_password="hashed",
        role="admin",
    )
    admin_only = require_roles("admin")

    with pytest.raises(HTTPException) as exc_info:
        admin_only(user)

    assert exc_info.value.status_code == 403
    assert admin_only(admin) is admin
