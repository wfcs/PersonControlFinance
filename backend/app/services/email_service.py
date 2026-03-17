"""Serviço de e-mail transacional via SendGrid."""

from __future__ import annotations

import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_client() -> SendGridAPIClient | None:
    if not settings.SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not configured — emails disabled")
        return None
    return SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Envia um e-mail genérico. Retorna True se enviou com sucesso."""
    client = _get_client()
    if client is None:
        logger.info("Email skipped (no API key): to=%s subject=%s", to_email, subject)
        return False

    message = Mail(
        from_email=Email(settings.EMAIL_FROM, "FinControl"),
        to_emails=To(to_email),
        subject=subject,
        html_content=Content("text/html", html_body),
    )

    try:
        response = client.send(message)
        logger.info("Email sent to=%s status=%s", to_email, response.status_code)
        return 200 <= response.status_code < 300
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


def send_welcome(to_email: str, full_name: str | None = None) -> bool:
    """E-mail de boas-vindas após registro."""
    name = full_name or to_email.split("@")[0]
    subject = "Bem-vindo ao FinControl!"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;">
        <h1 style="color:#1a1a2e;">Bem-vindo, {name}!</h1>
        <p>Sua conta no <strong>FinControl</strong> foi criada com sucesso.</p>
        <p>Comece conectando suas contas bancárias para ter controle total das suas finanças.</p>
        <a href="{settings.CORS_ORIGINS[0]}/dashboard"
           style="display:inline-block;padding:12px 24px;background:#6366f1;color:#fff;
                  text-decoration:none;border-radius:8px;margin-top:16px;">
            Acessar Dashboard
        </a>
        <p style="margin-top:32px;color:#666;font-size:13px;">
            Se você não criou esta conta, por favor ignore este e-mail.
        </p>
    </div>
    """
    return send_email(to_email, subject, html)


def send_password_reset(to_email: str, reset_url: str) -> bool:
    """E-mail de recuperação de senha."""
    subject = "Redefinir sua senha - FinControl"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;">
        <h1 style="color:#1a1a2e;">Redefinir Senha</h1>
        <p>Recebemos uma solicitação para redefinir sua senha no FinControl.</p>
        <a href="{reset_url}"
           style="display:inline-block;padding:12px 24px;background:#6366f1;color:#fff;
                  text-decoration:none;border-radius:8px;margin-top:16px;">
            Redefinir Senha
        </a>
        <p style="margin-top:24px;color:#666;font-size:13px;">
            Este link expira em 1 hora. Se você não solicitou a redefinição, ignore este e-mail.
        </p>
    </div>
    """
    return send_email(to_email, subject, html)


def send_plan_upgrade(to_email: str, full_name: str | None, plan: str) -> bool:
    """E-mail de confirmação de upgrade de plano."""
    name = full_name or to_email.split("@")[0]
    plan_display = {"pro": "Pro", "premium": "Premium"}.get(plan, plan.title())
    subject = f"Plano {plan_display} ativado - FinControl"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;">
        <h1 style="color:#1a1a2e;">Plano {plan_display} Ativado!</h1>
        <p>Olá {name},</p>
        <p>Seu plano <strong>{plan_display}</strong> está ativo. Aproveite todos os recursos:</p>
        <ul>
            <li>Contas ilimitadas</li>
            <li>Relatórios avançados</li>
            <li>Projeções financeiras</li>
            <li>Suporte prioritário</li>
        </ul>
        <a href="{settings.CORS_ORIGINS[0]}/dashboard"
           style="display:inline-block;padding:12px 24px;background:#6366f1;color:#fff;
                  text-decoration:none;border-radius:8px;margin-top:16px;">
            Acessar Dashboard
        </a>
    </div>
    """
    return send_email(to_email, subject, html)


def send_sync_error(to_email: str, full_name: str | None, error_detail: str) -> bool:
    """Notificação de erro na sincronização bancária."""
    name = full_name or to_email.split("@")[0]
    subject = "Atenção: Erro na sincronização - FinControl"
    html = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;">
        <h1 style="color:#dc2626;">Erro na Sincronização</h1>
        <p>Olá {name},</p>
        <p>Detectamos um problema ao sincronizar suas contas bancárias:</p>
        <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;margin:16px 0;">
            <p style="color:#991b1b;margin:0;">{error_detail}</p>
        </div>
        <p>Tente reconectar sua conta pelo dashboard.</p>
        <a href="{settings.CORS_ORIGINS[0]}/accounts"
           style="display:inline-block;padding:12px 24px;background:#6366f1;color:#fff;
                  text-decoration:none;border-radius:8px;margin-top:16px;">
            Gerenciar Contas
        </a>
    </div>
    """
    return send_email(to_email, subject, html)
