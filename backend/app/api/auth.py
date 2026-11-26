"""Authentication routes: register, login, refresh, profile."""

import uuid

import jwt
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.core.auth import CurrentUserDep
from app.core.db import SessionDep
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, session: SessionDep) -> User:
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login")
def login(body: LoginRequest, session: SessionDep) -> TokenResponse:
    user = session.exec(select(User).where(User.email == body.email)).first()

    # Intentionally vague — prevents email enumeration.
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
    )

    if user is None:
        raise credentials_error

    if not user.is_active:
        raise credentials_error

    if not verify_password(body.password, user.password_hash):
        raise credentials_error

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh")
def refresh(body: RefreshRequest, session: SessionDep) -> AccessTokenResponse:
    try:
        payload = decode_token(body.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired.",
        ) from None
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        ) from None

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expected a refresh token.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim.",
        )

    user = session.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
        )

    return AccessTokenResponse(
        access_token=create_access_token(str(user.id)),
    )


@router.get("/me", response_model=UserRead)
def me(user: CurrentUserDep) -> User:
    return user
