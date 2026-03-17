"""
Exemplo de implementação segura multi-tenant em um endpoint.

Este arquivo demonstra as boas práticas para implementar isolamento
multi-tenant em endpoints FastAPI.
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.core.deps import AuthUser, DBSession
from app.core.tenant_decorators import validate_tenant_access, require_tenant_context
from app.schemas.account import AccountCreate, AccountOut
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["Contas"])


# ─────────────────────────────────────────────────────────────────────────────
# ❌ EXEMPLO ERRADO - Não usar isto!
# ─────────────────────────────────────────────────────────────────────────────

async def list_all_accounts_insecure(db: DBSession):
    """
    ❌ ERRADO: Sem isolamento multi-tenant
    
    Problemas:
    1. Sem autenticação - qualquer um pode acessar
    2. Sem tenant_id - retorna contas de TODOS os tenants
    3. Sem decorator - fácil de esquecer security
    """
    from sqlalchemy import select
    from app.models.account import Account
    
    # Retorna TUDO!
    result = await db.execute(select(Account))
    return result.scalars().all()


# ─────────────────────────────────────────────────────────────────────────────
# ✅ EXEMPLO CORRETO - Use este padrão!
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[AccountOut])
@require_tenant_context  # Valida que contexto foi carregado
async def list_accounts(
    current_user: AuthUser,  # Requer autenticação (JWT válido)
    db: DBSession,
) -> list[AccountOut]:
    """
    ✅ CORRETO: Isolamento multi-tenant seguro
    
    Segurança:
    1. @require_tenant_context - Valida contexto
    2. current_user: AuthUser - Requer JWT válido
    3. Usa current_user.tenant_id - Garante isolamento
    4. RLS no banco - Dupla segurança
    """
    # Service passa tenant_id do usuário
    accounts = await account_service.list_accounts(
        tenant_id=current_user.tenant_id,
        db=db,
    )
    return [AccountOut.model_validate(a) for a in accounts]


@router.post("/", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
@require_tenant_context
async def create_account(
    data: AccountCreate,
    current_user: AuthUser,
    db: DBSession,
) -> AccountOut:
    """Cria nova conta para o tenant do usuário."""
    account = await account_service.create_account(
        data=data,
        tenant_id=current_user.tenant_id,  # ✅ IMPORTANT: sempre usar tenant do usuário
        db=db,
    )
    return AccountOut.model_validate(account)


@router.get("/{account_id}", response_model=AccountOut)
@require_tenant_context
async def get_account(
    account_id: UUID,
    current_user: AuthUser,
    db: DBSession,
) -> AccountOut:
    """
    Retorna uma conta específica.
    
    Nota: Não é necessário passar account_id na URL junto com tenant_id
    porque RLS filtra automaticamente por tenant_id.
    Se account_id não pertencer ao tenant do usuário, RLS retornará None.
    """
    account = await account_service.get_account(
        account_id=account_id,
        tenant_id=current_user.tenant_id,
        db=db,
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )
    
    return AccountOut.model_validate(account)


@router.patch("/{account_id}", response_model=AccountOut)
@require_tenant_context
async def update_account(
    account_id: UUID,
    data: AccountCreate,
    current_user: AuthUser,
    db: DBSession,
) -> AccountOut:
    """Atualiza uma conta do tenant do usuário."""
    account = await account_service.update_account(
        account_id=account_id,
        data=data,
        tenant_id=current_user.tenant_id,
        db=db,
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )
    
    return AccountOut.model_validate(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_tenant_context
async def delete_account(
    account_id: UUID,
    current_user: AuthUser,
    db: DBSession,
) -> None:
    """Deleta uma conta do tenant do usuário."""
    success = await account_service.delete_account(
        account_id=account_id,
        tenant_id=current_user.tenant_id,
        db=db,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )


# ─────────────────────────────────────────────────────────────────────────────
# EXEMPLO COM DECORATOR validate_tenant_access
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/{account_id}/details")
@validate_tenant_access("account_id")  # Valida que account_id pertence ao tenant
async def get_account_details(
    account_id: UUID,
    current_user: AuthUser,
    db: DBSession,
):
    """
    Exemplo usando validate_tenant_access.
    
    O decorator valida que o account_id solicitado
    pertence ao tenant do usuário ANTES de executar a função.
    """
    account = await account_service.get_account_with_details(
        account_id=account_id,
        tenant_id=current_user.tenant_id,
        db=db,
    )
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada",
        )
    
    return account


# ─────────────────────────────────────────────────────────────────────────────
# CHECKLIST DE SEGURANÇA
# ─────────────────────────────────────────────────────────────────────────────

"""
Antes de criar um novo endpoint, verificar:

□ Tem @require_tenant_context decorador?
□ Possui parâmetro current_user: AuthUser?
□ Passa current_user.tenant_id para o service?
□ Service filtra por tenant_id na query?
□ Retorna 404 ao invés de vazar dados de outro tenant?
□ Teste unitário valida isolamento?

Se todas as caixas estão marcadas, seu endpoint está seguro!
"""
