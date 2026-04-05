from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.models import User
from app.schemas.auth import UserRegister


def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()


def register_user(db: Session, data: UserRegister) -> User:
    existing_user = get_user_by_email(db, data.email)
    if existing_user is not None:
        raise ValueError("Email is already registered.")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
