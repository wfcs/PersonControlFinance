"""Categorização automática de transações por keywords."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.transaction import Transaction

# Keywords comuns de merchants brasileiros mapeadas para nomes de categoria
KEYWORD_RULES: dict[str, str] = {
    # Alimentação
    "supermercado": "Alimentação",
    "mercado": "Alimentação",
    "ifood": "Alimentação",
    "rappi": "Alimentação",
    "zé delivery": "Alimentação",
    "restaurante": "Alimentação",
    "padaria": "Alimentação",
    "açougue": "Alimentação",
    # Transporte
    "uber": "Transporte",
    "99": "Transporte",
    "cabify": "Transporte",
    "gasolina": "Transporte",
    "combustivel": "Transporte",
    "posto": "Transporte",
    "estacionamento": "Transporte",
    "pedagio": "Transporte",
    # Moradia
    "aluguel": "Moradia",
    "condominio": "Moradia",
    "energia": "Moradia",
    "cpfl": "Moradia",
    "enel": "Moradia",
    "sabesp": "Moradia",
    "agua": "Moradia",
    "gas": "Moradia",
    # Entretenimento
    "netflix": "Entretenimento",
    "spotify": "Entretenimento",
    "disney": "Entretenimento",
    "hbo": "Entretenimento",
    "prime video": "Entretenimento",
    "youtube": "Entretenimento",
    "steam": "Entretenimento",
    "cinema": "Entretenimento",
    # Saúde
    "farmacia": "Saúde",
    "drogaria": "Saúde",
    "hospital": "Saúde",
    "clinica": "Saúde",
    "laboratorio": "Saúde",
    "unimed": "Saúde",
    # Serviços
    "internet": "Serviços",
    "telefone": "Serviços",
    "celular": "Serviços",
    "claro": "Serviços",
    "vivo": "Serviços",
    "tim": "Serviços",
    # Educação
    "escola": "Educação",
    "faculdade": "Educação",
    "curso": "Educação",
    "udemy": "Educação",
    "alura": "Educação",
}


async def auto_categorize_transaction(
    tx: Transaction, tenant_id: UUID, db: AsyncSession
) -> UUID | None:
    """Tenta categorizar uma transação com base em keywords da descrição."""
    desc_lower = tx.description.lower()

    for keyword, category_name in KEYWORD_RULES.items():
        if keyword in desc_lower:
            cat = await db.scalar(
                select(Category).where(
                    Category.tenant_id == tenant_id,
                    Category.name.ilike(f"%{category_name}%"),
                )
            )
            if cat:
                return cat.id

    return None


async def auto_categorize_uncategorized(tenant_id: UUID, db: AsyncSession) -> int:
    """Categoriza todas as transações sem categoria do tenant."""
    uncategorized = (
        await db.scalars(
            select(Transaction).where(
                Transaction.tenant_id == tenant_id,
                Transaction.category_id.is_(None),
            )
        )
    ).all()

    categorized = 0
    for tx in uncategorized:
        cat_id = await auto_categorize_transaction(tx, tenant_id, db)
        if cat_id:
            tx.category_id = cat_id
            categorized += 1

    if categorized:
        await db.flush()

    return categorized
