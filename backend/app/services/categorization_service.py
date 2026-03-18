"""Auto-categorization engine based on keyword rules."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category

# Keyword -> category name mapping (case-insensitive matching)
KEYWORD_RULES: dict[str, str] = {
    # Transporte
    "uber": "Transporte",
    "99": "Transporte",
    "cabify": "Transporte",
    "lyft": "Transporte",
    "combustivel": "Transporte",
    "gasolina": "Transporte",
    "estacionamento": "Transporte",
    "pedagio": "Transporte",
    # Alimentacao
    "ifood": "Alimentacao",
    "rappi": "Alimentacao",
    "restaurante": "Alimentacao",
    "supermercado": "Alimentacao",
    "mercado": "Alimentacao",
    "padaria": "Alimentacao",
    "lanchonete": "Alimentacao",
    # Entretenimento
    "netflix": "Entretenimento",
    "spotify": "Entretenimento",
    "disney": "Entretenimento",
    "hbo": "Entretenimento",
    "amazon prime": "Entretenimento",
    "cinema": "Entretenimento",
    "teatro": "Entretenimento",
    # Moradia
    "aluguel": "Moradia",
    "condominio": "Moradia",
    "iptu": "Moradia",
    "energia": "Moradia",
    "luz": "Moradia",
    "agua": "Moradia",
    "gas": "Moradia",
    "internet": "Moradia",
    # Saude
    "farmacia": "Saude",
    "hospital": "Saude",
    "medico": "Saude",
    "consulta": "Saude",
    "plano de saude": "Saude",
    # Educacao
    "escola": "Educacao",
    "faculdade": "Educacao",
    "curso": "Educacao",
    "livro": "Educacao",
    "udemy": "Educacao",
    # Salario
    "salario": "Salario",
    "pagamento": "Salario",
    "holerite": "Salario",
}


async def auto_categorize(
    description: str,
    tenant_id: str,
    db: AsyncSession,
) -> str | None:
    """Try to match a transaction description to a category via keyword rules.

    Returns the category_id (as string) if a match is found, None otherwise.
    """
    desc_lower = description.lower()

    matched_category_name: str | None = None
    for keyword, cat_name in KEYWORD_RULES.items():
        if keyword in desc_lower:
            matched_category_name = cat_name
            break

    if matched_category_name is None:
        return None

    # Look up the category by name for this tenant
    from uuid import UUID

    tid = UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
    result = await db.execute(
        select(Category).where(
            Category.tenant_id == tid,
            Category.name == matched_category_name,
        )
    )
    category = result.scalar_one_or_none()
    if category is None:
        return None

    return str(category.id)


async def categorize_transaction(
    transaction_description: str,
    tenant_id: str,
    db: AsyncSession,
    current_category_id: str | None = None,
) -> str | None:
    """Apply auto-categorization to a transaction if no category_id is set.

    Returns the category_id to use (either existing or auto-detected).
    """
    if current_category_id is not None:
        return current_category_id
    return await auto_categorize(transaction_description, tenant_id, db)
