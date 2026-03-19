from __future__ import annotations

import json
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_action(
    session: AsyncSession,
    tenant_id: UUID,
    action: str,
    entity_type: str,
    entity_id: str,
    user_id: Optional[UUID] = None,
    changes: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Record an audit log entry."""
    entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        changes=json.dumps(changes) if changes else None,
        ip_address=ip_address,
    )
    session.add(entry)
    await session.flush()
    return entry


async def list_audit_logs(
    tenant_id: UUID,
    session: AsyncSession,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AuditLog]:
    """List audit logs for a tenant with optional filters."""
    query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())
