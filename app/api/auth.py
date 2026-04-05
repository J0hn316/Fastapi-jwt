from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import TokenOut, UserLogin, UserOut, UserRegister
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_route(payload: UserRegister, db: Session = Depends(get_db)) -> UserOut:
    try:
        user = register_user(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return user


@router.post("/login", response_model=TokenOut)
def login_route(payload: UserLogin, db: Session = Depends(get_db)) -> TokenOut:
    user = authenticate_user(db, payload.email, payload.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    access_token = create_access_token(subject=str(user.id))
    return TokenOut(access_token=access_token)
