from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models.account import Account
from app.models.user import User
from app.schemas.pluggy import (
    ConnectTokenRequest,
    ConnectTokenResponse,
    ItemConnectedRequest,
    PluggyStatusResponse,
    SyncResponse,
)

router = APIRouter(prefix="/open-finance", tags=["Open Finance"])


def _check_pluggy_configured() -> None:
    from app.core.config import settings
    if not settings.PLUGGY_CLIENT_ID or not settings.PLUGGY_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Open Finance não está configurado. Configure PLUGGY_CLIENT_ID e PLUGGY_CLIENT_SECRET.",
        )


@router.get("/status", response_model=PluggyStatusResponse)
async def pluggy_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PluggyStatusResponse:
    """Check Open Finance configuration and connection status."""
    from app.core.config import settings
    configured = bool(settings.PLUGGY_CLIENT_ID and settings.PLUGGY_CLIENT_SECRET)

    # Count accounts with pluggy_item_id
    result = await session.execute(
        select(func.count()).where(
            Account.tenant_id == current_user.tenant_id,
            Account.pluggy_item_id.isnot(None),
        )
    )
    connected = result.scalar() or 0

    return PluggyStatusResponse(configured=configured, connected_items=connected)


@router.post("/connect-token", response_model=ConnectTokenResponse)
async def create_connect_token(
    data: ConnectTokenRequest,
    current_user: User = Depends(get_current_user),
) -> ConnectTokenResponse:
    """Generate a Pluggy Connect Widget token."""
    _check_pluggy_configured()

    if os.environ.get("TESTING") == "1":
        return ConnectTokenResponse(access_token="test_connect_token_123")

    from app.services.pluggy_client import create_connect_token as _create
    token = await _create(item_id=data.item_id)
    return ConnectTokenResponse(access_token=token)


@router.post("/connect", response_model=SyncResponse)
async def on_item_connected(
    data: ItemConnectedRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SyncResponse:
    """Called after user connects a bank via Pluggy widget.

    Syncs accounts and transactions from the connected item.
    """
    _check_pluggy_configured()

    if os.environ.get("TESTING") == "1":
        return SyncResponse(accounts_synced=0, transactions_imported=0)

    from app.services.pluggy_sync_service import sync_full_item
    result = await sync_full_item(
        item_id=data.item_id,
        tenant_id=current_user.tenant_id,
        session=session,
    )
    return SyncResponse(**result)


@router.post("/sync/{item_id}", response_model=SyncResponse)
async def sync_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SyncResponse:
    """Manually trigger sync for a specific connected item."""
    _check_pluggy_configured()

    if os.environ.get("TESTING") == "1":
        return SyncResponse(accounts_synced=0, transactions_imported=0)

    from app.services.pluggy_sync_service import sync_full_item
    result = await sync_full_item(
        item_id=item_id,
        tenant_id=current_user.tenant_id,
        session=session,
    )
    return SyncResponse(**result)


@router.delete("/disconnect/{item_id}")
async def disconnect_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Disconnect a bank (delete Pluggy item and unlink accounts)."""
    _check_pluggy_configured()

    # Unlink local accounts
    result = await session.execute(
        select(Account).where(
            Account.tenant_id == current_user.tenant_id,
            Account.pluggy_item_id == item_id,
        )
    )
    accounts = result.scalars().all()
    for acc in accounts:
        acc.pluggy_item_id = None
    await session.flush()

    # Delete from Pluggy (skip in tests)
    if os.environ.get("TESTING") != "1":
        from app.services.pluggy_client import delete_item
        await delete_item(item_id)

    return {"status": "disconnected", "accounts_unlinked": len(accounts)}
