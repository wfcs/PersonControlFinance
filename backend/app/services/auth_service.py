from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


async def register(data: RegisterRequest, db: AsyncSession) -> TokenResponse:
    # Verifica e-mail duplicado
    existing = await db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    # Cria tenant individual para o usuário
    tenant = Tenant(name=data.full_name or data.email.split("@")[0])
    db.add(tenant)
    await db.flush()  # garante tenant.id antes de criar o user

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        tenant_id=tenant.id,
    )
    db.add(user)
    await db.flush()

    # Envia e-mail de boas-vindas em background (Celery)
    import logging
    import os

    if os.getenv("TESTING") != "1":
        try:
            from app.workers.tasks import send_welcome_email

            send_welcome_email.delay(data.email, data.full_name)
        except Exception:
            logging.getLogger(__name__).debug("Celery unavailable, skipping welcome email")

    return _build_tokens(user.id, tenant.id, user.email)


async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == data.email))

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta desativada")

    return _build_tokens(user.id, user.tenant_id, user.email)


async def refresh(refresh_token: str, db: AsyncSession) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token incorreto")

    user_id = UUID(payload["sub"])
    user = await db.get(User, user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    return _build_tokens(user.id, user.tenant_id, user.email)


def _build_tokens(user_id: UUID, tenant_id: UUID, email: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user_id, tenant_id, {"email": email}),
        refresh_token=create_refresh_token(user_id, tenant_id),
    )
