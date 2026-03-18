"""Authentication endpoints: register, login, refresh, logout."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import authenticate_user, refresh_tokens, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and tenant",
)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_user(payload, db)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive tokens",
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(payload.email, payload.password, db)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh an expired access token",
)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_tokens(payload.refresh_token, db)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout (client-side token discard)",
)
async def logout():
    """Logout is handled client-side by discarding tokens.

    A server-side token blocklist can be added later with Redis.
    """
    return {"detail": "Successfully logged out"}
