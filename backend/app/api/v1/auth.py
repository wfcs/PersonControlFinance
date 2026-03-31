from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.core.security import create_access_token, create_refresh_token
from app.services.auth_service import login_user, refresh_access_token, register_user

# Inherit from main app's limiter or create a local one with same config
storage_uri = settings.REDIS_URL
if storage_uri.startswith("memory://") or settings.ENVIRONMENT == "development":
    storage_uri = "memory://"

limiter = Limiter(key_func=get_remote_address, storage_uri=storage_uri)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


@router.post("/register", response_model=dict, status_code=201)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def register(
    request: Request,
    response: Response,
    data: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    user = await register_user(data, session)

    # Login automático após registro
    tokens = TokenResponse(
        access_token=create_access_token(user.id, user.tenant_id),
        refresh_token=create_refresh_token(user.id, user.tenant_id)
    )
    _set_auth_cookies(response, tokens)

    return {"status": "success", "user": user}


@router.post("/login")
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    tokens = await login_user(data, session)
    _set_auth_cookies(response, tokens)

    # Buscar usuário para retornar no body
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one()

    return {"status": "success", "user": UserResponse.model_validate(user)}


@router.post("/refresh")
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def refresh(
    request: Request,
    response: Response,
    data: RefreshRequest | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict:
    # Try to get refresh token from cookie first
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token and data:
        refresh_token = data.refresh_token

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    tokens = await refresh_access_token(RefreshRequest(refresh_token=refresh_token), session)
    _set_auth_cookies(response, tokens)
    return {"status": "success"}


@router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "success"}


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
