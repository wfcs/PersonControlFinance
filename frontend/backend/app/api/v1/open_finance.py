"""Endpoints de Open Finance (Pluggy)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import AuthUser, DBSession
from app.integrations.pluggy_client import pluggy_client
from app.models.account import Account
from app.schemas.pluggy import ConnectTokenRequest, ConnectTokenResponse
from app.services import pluggy_service

router = APIRouter(prefix="/open-finance", tags=["Open Finance"])


@router.post("/connect-token", response_model=ConnectTokenResponse)
async def create_connect_token(
    data: ConnectTokenRequest, current_user: AuthUser, db: DBSession
) -> ConnectTokenResponse:
    """Gera token para abrir o widget Pluggy Connect no front-end."""
    result = await pluggy_service.create_connect_token(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        db=db,
        item_id=data.item_id,
    )
    return ConnectTokenResponse(access_token=result["accessToken"])


@router.post("/sync/{item_id}")
async def trigger_sync(
    item_id: str, current_user: AuthUser, db: DBSession
) -> dict:
    """Dispara sincronização manual de um item Pluggy."""
    # Verificar que o item pertence ao tenant
    acc = await db.scalar(
        select(Account).where(
            Account.pluggy_item_id == item_id,
            Account.tenant_id == current_user.tenant_id,
        )
    )
    if not acc:
        # Item novo — primeiro sync
        pass

    accounts = await pluggy_service.sync_item_accounts(
        item_id, current_user.tenant_id, db
    )
    tx_count = await pluggy_service.sync_item_transactions(
        item_id, current_user.tenant_id, db
    )
    return {
        "accounts_synced": len(accounts),
        "transactions_synced": tx_count,
    }


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_item(
    item_id: str, current_user: AuthUser, db: DBSession
) -> None:
    """Desconecta um item Pluggy e desativa suas contas."""
    accounts = (
        await db.scalars(
            select(Account).where(
                Account.pluggy_item_id == item_id,
                Account.tenant_id == current_user.tenant_id,
            )
        )
    ).all()

    if not accounts:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    for acc in accounts:
        acc.is_active = False

    try:
        await pluggy_client.delete_item(item_id)
    except Exception:
        pass  # Item pode já estar deletado no Pluggy
