"""Initial schema with RLS policies for multi-tenancy.

Revision ID: 0001
Revises:
Create Date: 2026-03-18

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Tables that require RLS (all tenant-scoped tables)
RLS_TABLES = [
    "users",
    "accounts",
    "transactions",
    "categories",
    "goals",
    "recurrences",
    "webhook_logs",
]


def upgrade() -> None:
    # ── tenants ───────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("plan", sa.String(50), nullable=False, server_default="free"),
        sa.Column("subscription_status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    # ── users ─────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_tenant_id_id", "users", ["tenant_id", "id"])
    op.create_index("ix_users_tenant_id_email", "users", ["tenant_id", "email"])

    # ── accounts ──────────────────────────────────────────────
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("institution", sa.String(255), nullable=True),
        sa.Column("balance", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="BRL"),
        sa.Column("pluggy_account_id", sa.String(255), nullable=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_accounts_tenant_id", "accounts", ["tenant_id"])
    op.create_index("ix_accounts_tenant_id_id", "accounts", ["tenant_id", "id"])
    op.create_index("ix_accounts_tenant_id_type", "accounts", ["tenant_id", "type"])

    # ── categories ────────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("budget_limit", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_categories_tenant_id", "categories", ["tenant_id"])
    op.create_index("ix_categories_tenant_id_id", "categories", ["tenant_id", "id"])
    op.create_index("ix_categories_tenant_id_type", "categories", ["tenant_id", "type"])

    # ── transactions ──────────────────────────────────────────
    op.create_table(
        "transactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_transactions_account_id", "transactions", ["account_id"])
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_tenant_id", "transactions", ["tenant_id"])
    op.create_index("ix_transactions_tenant_id_id", "transactions", ["tenant_id", "id"])
    op.create_index("ix_transactions_tenant_id_date", "transactions", ["tenant_id", "date"])
    op.create_index("ix_transactions_tenant_id_type", "transactions", ["tenant_id", "type"])
    op.create_index("ix_transactions_tenant_id_account_id", "transactions", ["tenant_id", "account_id"])

    # ── goals ─────────────────────────────────────────────────
    op.create_table(
        "goals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("target_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("current_amount", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="in_progress"),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_goals_tenant_id", "goals", ["tenant_id"])
    op.create_index("ix_goals_tenant_id_id", "goals", ["tenant_id", "id"])
    op.create_index("ix_goals_tenant_id_status", "goals", ["tenant_id", "status"])

    # ── recurrences ───────────────────────────────────────────
    op.create_table(
        "recurrences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("frequency", sa.String(20), nullable=False),
        sa.Column("next_due_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_recurrences_account_id", "recurrences", ["account_id"])
    op.create_index("ix_recurrences_category_id", "recurrences", ["category_id"])
    op.create_index("ix_recurrences_tenant_id", "recurrences", ["tenant_id"])
    op.create_index("ix_recurrences_tenant_id_id", "recurrences", ["tenant_id", "id"])
    op.create_index("ix_recurrences_tenant_id_next_due_date", "recurrences", ["tenant_id", "next_due_date"])

    # ── webhook_logs ──────────────────────────────────────────
    op.create_table(
        "webhook_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(200), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="received"),
        sa.Column("tenant_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_webhook_logs_tenant_id", "webhook_logs", ["tenant_id"])
    op.create_index("ix_webhook_logs_tenant_id_id", "webhook_logs", ["tenant_id", "id"])
    op.create_index("ix_webhook_logs_tenant_id_source", "webhook_logs", ["tenant_id", "source"])

    # ── Row-Level Security (PostgreSQL only) ──────────────────
    # Enable RLS on all tenant-scoped tables and create isolation policies.
    # These raw SQL statements are PostgreSQL-specific and will be skipped
    # when running against SQLite (tests).
    for table in RLS_TABLES:
        # Enable RLS on the table
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")

        # Force RLS for table owner as well (prevents bypassing)
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

        # For webhook_logs, tenant_id is nullable so handle NULLs
        if table == "webhook_logs":
            using_clause = (
                "(tenant_id IS NULL OR tenant_id::text = current_setting('app.current_tenant_id', true))"
            )
        else:
            using_clause = (
                "tenant_id::text = current_setting('app.current_tenant_id', true)"
            )

        # Create the tenant isolation policy
        op.execute(
            f"CREATE POLICY tenant_isolation_policy ON {table} "
            f"FOR ALL "
            f"USING ({using_clause}) "
            f"WITH CHECK ({using_clause})"
        )


def downgrade() -> None:
    # ── Drop RLS policies ─────────────────────────────────────
    for table in reversed(RLS_TABLES):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    # ── Drop tables in reverse dependency order ───────────────
    op.drop_table("webhook_logs")
    op.drop_table("recurrences")
    op.drop_table("goals")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("accounts")
    op.drop_table("users")
    op.drop_table("tenants")
