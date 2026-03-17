"""Testes do serviço de e-mail e endpoints de notificação."""

import pytest
from httpx import AsyncClient


# ── Email service (unit) ──────────────────────────────────────────────────────

def test_send_email_without_api_key():
    """Sem SENDGRID_API_KEY, send_email retorna False sem erro."""
    from app.services.email_service import send_email

    result = send_email("test@example.com", "Test", "<p>Hello</p>")
    assert result is False


def test_send_welcome_without_api_key():
    """send_welcome retorna False sem erro quando não há API key."""
    from app.services.email_service import send_welcome

    result = send_welcome("test@example.com", "Test User")
    assert result is False


def test_send_plan_upgrade_without_api_key():
    """send_plan_upgrade retorna False sem erro quando não há API key."""
    from app.services.email_service import send_plan_upgrade

    result = send_plan_upgrade("test@example.com", "User", "pro")
    assert result is False


# ── Notification endpoints ────────────────────────────────────────────────────

async def test_send_test_email_requires_auth(client: AsyncClient):
    """POST /notifications/send-test sem token retorna 403."""
    res = await client.post("/api/v1/notifications/send-test")
    assert res.status_code in (401, 403)


async def test_resend_welcome_requires_auth(client: AsyncClient):
    """POST /notifications/resend-welcome sem token retorna 403."""
    res = await client.post("/api/v1/notifications/resend-welcome")
    assert res.status_code in (401, 403)
