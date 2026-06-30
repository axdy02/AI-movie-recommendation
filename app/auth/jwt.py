from datetime import datetime, timedelta, timezone
from collections.abc import Mapping
from typing import Any

from jose import JWTError, jwt

from app.config import settings


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    claims: Mapping[str, Any] | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = dict(claims or {})
    payload.update({"sub": subject, "exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError("Invalid access token.") from exc
