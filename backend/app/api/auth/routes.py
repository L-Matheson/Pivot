"""Authentication routes: register, login, refresh, logout, profile."""

import uuid

import jwt
from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlmodel import select

from app.core.auth import CurrentUserDep
from app.core.config import settings
from app.core.cookies import clear_refresh_cookie, set_refresh_cookie
from app.core.db import SessionDep
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.token_store import (
    is_refresh_token_valid,
    revoke_refresh_token,
    store_refresh_token,
)
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RegisterRequest,
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
def login(body: LoginRequest, session: SessionDep, response: Response) -> AccessTokenResponse:
    user = session.exec(select(User).where(User.email == body.email)).first()

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

    access_token = create_access_token(str(user.id))
    refresh_token, jti = create_refresh_token(str(user.id))
    store_refresh_token(jti, str(user.id))
    set_refresh_cookie(response, refresh_token)

    return AccessTokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh")
def refresh(request: Request, session: SessionDep, response: Response) -> AccessTokenResponse:
    token = request.cookies.get(settings.cookie_name_refresh)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token.",
        )

    try:
        payload = decode_token(token)
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

    jti = payload.get("jti")
    if not jti or not is_refresh_token_valid(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim.",
        )

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject.",
        ) from None

    user = session.get(User, user_uuid)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
        )

    revoke_refresh_token(jti)

    new_access = create_access_token(str(user.id))
    new_refresh, new_jti = create_refresh_token(str(user.id))
    store_refresh_token(new_jti, str(user.id))
    set_refresh_cookie(response, new_refresh)

    return AccessTokenResponse(
        access_token=new_access,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response) -> None:
    token = request.cookies.get(settings.cookie_name_refresh)
    if token:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            if jti:
                revoke_refresh_token(jti)
        except jwt.PyJWTError:
            pass
    clear_refresh_cookie(response)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUserDep) -> User:
    return user
