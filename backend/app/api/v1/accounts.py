"""Account CRUD endpoints with Pluggy integration."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.plan_guard import check_resource_limit, require_feature
from app.integrations.pluggy_client import PluggyClient
from app.models.account import Account
from app.models.user import User
from app.schemas.account import (
    AccountCreate,
    AccountRead,
    AccountUpdate,
    PluggyConnectRequest,
    PluggyConnectResponse,
)
from app.services.account_service import sync_from_pluggy

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountRead])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all accounts for the current tenant."""
    result = await db.execute(
        select(Account)
        .where(Account.tenant_id == current_user.tenant_id)
        .order_by(Account.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a manual account (checks plan limit)."""
    await check_resource_limit(db, current_user.tenant_id, "accounts", Account)

    account = Account(
        name=payload.name,
        type=payload.type,
        institution=payload.institution,
        balance=payload.balance,
        currency=payload.currency,
        tenant_id=current_user.tenant_id,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get an account by ID."""
    result = await db.execute(
        select(Account).where(
            Account.id == account_id,
            Account.tenant_id == current_user.tenant_id,
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: UUID,
    payload: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an account."""
    result = await db.execute(
        select(Account).where(
            Account.id == account_id,
            Account.tenant_id == current_user.tenant_id,
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    await db.commit()
    await db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_200_OK)
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an account."""
    result = await db.execute(
        select(Account).where(
            Account.id == account_id,
            Account.tenant_id == current_user.tenant_id,
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    await db.delete(account)
    await db.commit()
    return {"detail": "Account deleted"}


@router.post(
    "/connect",
    response_model=PluggyConnectResponse,
    dependencies=[Depends(require_feature("open_finance"))],
)
async def get_pluggy_connect_token(
    payload: PluggyConnectRequest,
    current_user: User = Depends(get_current_user),
):
    """Get a Pluggy connect token (Pro+ plan required)."""
    client = PluggyClient()
    token = await client.create_connect_token(item_id=payload.item_id)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to obtain Pluggy connect token",
        )
    return PluggyConnectResponse(connect_token=token)


@router.post("/sync/{item_id}", dependencies=[Depends(require_feature("open_finance"))])
async def sync_pluggy_accounts(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger sync of accounts/transactions from Pluggy."""
    result = await sync_from_pluggy(item_id, str(current_user.tenant_id), db)
    return result
