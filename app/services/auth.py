from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.auth.passwords import hash_password, verify_password
from app.config import settings
from app.models.user import User
from app.schemas.auth import RegisterRequest, Token


class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        normalized_email = email.strip().lower()
        return db.scalar(
            select(User).where(func.lower(User.email) == normalized_email),
        )

    @classmethod
    def register_user(cls, db: Session, payload: RegisterRequest) -> User:
        normalized_email = payload.email.strip().lower()
        existing_user = cls.get_user_by_email(db, normalized_email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = User(
            email=normalized_email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            role="user",
            is_active=True,
        )
        try:
            db.add(user)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            ) from None

        db.refresh(user)
        return user

    @classmethod
    def authenticate_user(
        cls,
        db: Session,
        email: str,
        password: str,
    ) -> User | None:
        user = cls.get_user_by_email(db, email)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_token_for_user(user: User) -> Token:
        access_token = create_access_token(
            subject=str(user.id),
            claims={"role": user.role},
        )
        return Token(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )
