"""Add composite indexes for tenant-scoped tables.

Revision ID: 002
Revises: 001
"""
from __future__ import annotations

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

TABLES = [
    "accounts",
    "transactions",
    "categories",
    "goals",
    "invoices",
    "recurrences",
    "webhook_logs",
]


def upgrade() -> None:
    for table in TABLES:
        op.create_index(
            f"ix_{table}_tenant_id_id",
            table,
            ["tenant_id", "id"],
        )


def downgrade() -> None:
    for table in TABLES:
        op.drop_index(f"ix_{table}_tenant_id_id", table_name=table)
