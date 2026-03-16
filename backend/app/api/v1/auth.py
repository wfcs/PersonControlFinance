from fastapi import APIRouter, status

from app.core.deps import AuthUser, DBSession
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DBSession) -> TokenResponse:
    """Cria novo usuário + tenant e retorna tokens."""
    return await auth_service.register(data, db)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DBSession) -> TokenResponse:
    """Autentica e retorna access + refresh token."""
    return await auth_service.login(data, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: DBSession) -> TokenResponse:
    """Gera novo access token a partir do refresh token."""
    return await auth_service.refresh(data.refresh_token, db)


@router.get("/me", response_model=UserOut)
async def me(current_user: AuthUser, db: DBSession) -> UserOut:
    """Retorna dados do usuário autenticado."""
    from sqlalchemy import select
    from app.models.user import User

    user = await db.scalar(select(User).where(User.id == current_user.user_id))
    return UserOut.model_validate(user)
