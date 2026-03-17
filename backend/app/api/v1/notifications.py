"""Endpoints de notificações por e-mail."""

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, status

from app.core.deps import AuthUser, DBSession

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class SendEmailRequest(BaseModel):
    subject: str
    html_body: str


class NotificationResponse(BaseModel):
    status: str
    message: str


@router.post("/send-test", response_model=NotificationResponse)
async def send_test_email(current_user: AuthUser) -> NotificationResponse:
    """Envia um e-mail de teste para o usuário autenticado."""
    from app.workers.tasks import send_notification

    send_notification.delay(
        current_user.email,
        "Teste de notificação - FinControl",
        "<h1>Teste</h1><p>Este é um e-mail de teste do FinControl.</p>",
    )
    return NotificationResponse(status="queued", message="E-mail de teste enviado para fila")


@router.post("/resend-welcome", response_model=NotificationResponse)
async def resend_welcome(current_user: AuthUser, db: DBSession) -> NotificationResponse:
    """Reenvia o e-mail de boas-vindas."""
    from sqlalchemy import select

    from app.models.user import User
    from app.workers.tasks import send_welcome_email

    user = await db.scalar(select(User).where(User.id == current_user.user_id))
    if user:
        send_welcome_email.delay(user.email, user.full_name)

    return NotificationResponse(status="queued", message="E-mail de boas-vindas reenviado")
