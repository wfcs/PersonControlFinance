"""Enable Row-Level Security on tenant-scoped tables.

Revision ID: 003
Revises: 002

NOTE: RLS is PostgreSQL-only. This migration is a no-op on SQLite.
"""
from __future__ import annotations

from alembic import op

revision = "003"
down_revision = "002"
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
    conn = op.get_bind()
    if conn.dialect.name != "postgresql":
        return

    # Create app_user role if it doesn't exist
    op.execute(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN "
        "CREATE ROLE app_user; "
        "END IF; "
        "END $$;"
    )

    for table in TABLES:
        # Enable RLS
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

        # Grant access to app_user
        op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO app_user;")

        # Create policy: rows visible only when tenant_id matches session variable
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"USING (tenant_id::text = current_setting('app.current_tenant_id', true));"
        )


def downgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name != "postgresql":
        return

    for table in TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
