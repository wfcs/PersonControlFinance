"""Testes de isolamento multi-tenant e RLS."""

import pytest
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.tenant import Tenant
from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.core.tenant_context import apply_tenant_context, clear_tenant_context
from app.core.security import hash_password


@pytest.fixture(scope="function")
async def tenant1():
    """Primeiro tenant para testes."""
    tenant = Tenant(id=uuid4(), name="Tenant 1", plan="pro")
    return tenant


@pytest.fixture(scope="function")
async def tenant2():
    """Segundo tenant para testes."""
    tenant = Tenant(id=uuid4(), name="Tenant 2", plan="pro")
    return tenant


@pytest.fixture(scope="function")
async def user1(tenant1):
    """Usuário do tenant 1."""
    user = User(
        id=uuid4(),
        email="user1@tenant1.com",
        hashed_password=hash_password("password123"),
        full_name="User 1",
        tenant_id=tenant1.id,
    )
    return user


@pytest.fixture(scope="function")
async def user2(tenant2):
    """Usuário do tenant 2."""
    user = User(
        id=uuid4(),
        email="user2@tenant2.com",
        hashed_password=hash_password("password123"),
        full_name="User 2",
        tenant_id=tenant2.id,
    )
    return user


@pytest.mark.asyncio
async def test_rls_prevents_cross_tenant_select(
    db_session: AsyncSession, tenant1, tenant2, user1, user2
):
    """
    Testa se RLS impede leitura de dados de outro tenant.
    """
    # Adicionar tenants e usuários ao banco
    db_session.add(tenant1)
    db_session.add(tenant2)
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # Criar categorias para cada tenant
    cat1 = Category(
        id=uuid4(),
        name="Supermercado",
        color="#FF0000",
        tenant_id=tenant1.id,
    )
    cat2 = Category(
        id=uuid4(),
        name="Gasolina",
        color="#00FF00",
        tenant_id=tenant2.id,
    )

    db_session.add(cat1)
    db_session.add(cat2)
    await db_session.commit()

    # Aplicar contexto do user1 (tenant 1)
    await apply_tenant_context(db_session, tenant1.id, user1.id)

    # Executar query - deve retornar apenas 1 categoria
    from sqlalchemy import select

    result = await db_session.execute(select(Category))
    categories = result.scalars().all()

    assert len(categories) == 1
    assert categories[0].id == cat1.id
    assert categories[0].tenant_id == tenant1.id

    # Limpar
    await clear_tenant_context(db_session)


@pytest.mark.asyncio
async def test_rls_prevents_cross_tenant_insert(
    db_session: AsyncSession, tenant1, tenant2, user1
):
    """
    Testa se RLS impede inserção de dados com tenant_id diferente.
    """
    # Adicionar tenants
    db_session.add(tenant1)
    db_session.add(tenant2)
    await db_session.commit()

    # Aplicar contexto do user1 (tenant 1)
    await apply_tenant_context(db_session, tenant1.id, user1.id)

    # Tentar inserir categoria com tenant_id != user1.tenant_id
    # Isso deveria ser bloqueado pelo RLS
    cat = Category(
        id=uuid4(),
        name="Maledicta",
        color="#FF0000",
        tenant_id=tenant2.id,  # tenant diferente!
    )

    db_session.add(cat)

    # RLS deveria bloquear com uma exception
    with pytest.raises(Exception):  # ProgrammingError ou similar
        await db_session.commit()

    await clear_tenant_context(db_session)


@pytest.mark.asyncio
async def test_context_variables_isolation(tenant1, user1):
    """
    Testa se context variables mantêm isolamento entre requests.
    """
    from app.core.tenant_context import get_current_tenant_id, get_current_user_id

    # Inicialmente vazios
    assert get_current_tenant_id() is None
    assert get_current_user_id() is None

    # Depois de set, devem estar preenchidos
    tenant_uuid = uuid4()
    user_uuid = uuid4()

    from app.core.tenant_context import set_current_tenant_id, set_current_user_id

    set_current_tenant_id(tenant_uuid)
    set_current_user_id(user_uuid)

    assert get_current_tenant_id() == tenant_uuid
    assert get_current_user_id() == user_uuid


@pytest.mark.asyncio
async def test_tenant_isolation_account_creation(
    db_session: AsyncSession, tenant1, tenant2, user1, user2
):
    """
    Testa se contas criadas por user1 só são visíveis para tenant1.
    """
    # Setup
    db_session.add(tenant1)
    db_session.add(tenant2)
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # User1 cria uma conta
    await apply_tenant_context(db_session, tenant1.id, user1.id)

    account1 = Account(
        id=uuid4(),
        name="Conta Bancária",
        institution_name="Banco XYZ",
        type="checking",
        tenant_id=tenant1.id,
        balance=1000,
    )
    db_session.add(account1)
    await db_session.commit()

    # Checar que user1 vê a conta
    from sqlalchemy import select

    result = await db_session.execute(select(Account))
    accounts = result.scalars().all()
    assert len(accounts) == 1

    await clear_tenant_context(db_session)

    # User2 não deveria ver conta de user1
    await apply_tenant_context(db_session, tenant2.id, user2.id)

    result = await db_session.execute(select(Account))
    accounts = result.scalars().all()
    # RLS deveria retornar lista vazia
    assert len(accounts) == 0

    await clear_tenant_context(db_session)


@pytest.mark.asyncio
async def test_missing_tenant_context_fails(
    db_session: AsyncSession, tenant1
):
    """
    Testa se operações sem tenant context falham.
    """
    db_session.add(tenant1)
    await db_session.commit()

    # Tentar query sem context
    from sqlalchemy import select

    result = await db_session.execute(select(Category))
    # Sem tenant context setado, RLS deveria retornar vazio ou erro
    categories = result.scalars().all()
    assert len(categories) == 0
