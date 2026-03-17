"""Add RLS (Row-Level Security) policies for multi-tenant isolation.

Revision ID: 0003_rls_policies
Revises: 0002_webhook_logs
Create Date: 2026-03-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_rls_policies"
down_revision = "0002_webhook_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar função para comparar tenant_id
    op.execute("""
    CREATE OR REPLACE FUNCTION get_current_tenant_id() RETURNS UUID AS $$
        SELECT COALESCE(
            current_setting('app.current_tenant_id', true),
            '00000000-0000-0000-0000-000000000000'::uuid
        )::uuid;
    $$ LANGUAGE SQL STABLE;
    """)

    # Habilitar RLS em todas as tabelas tenant-aware
    tables_with_rls = [
        "users",
        "accounts",
        "transactions",
        "categories",
        "recurrences",
        "webhook_logs",
    ]

    for table_name in tables_with_rls:
        # Habilitar RLS
        op.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")

        # Policy de SELECT: usuários só veem dados do seu tenant
        op.execute(f"""
        CREATE POLICY {table_name}_tenant_isolation_select ON {table_name}
        FOR SELECT
        USING (tenant_id = get_current_tenant_id());
        """)

        # Policy de INSERT: dados devem ser do tenant do usuário
        op.execute(f"""
        CREATE POLICY {table_name}_tenant_isolation_insert ON {table_name}
        FOR INSERT
        WITH CHECK (tenant_id = get_current_tenant_id());
        """)

        # Policy de UPDATE: só pode atualizar dados do seu tenant
        op.execute(f"""
        CREATE POLICY {table_name}_tenant_isolation_update ON {table_name}
        FOR UPDATE
        USING (tenant_id = get_current_tenant_id())
        WITH CHECK (tenant_id = get_current_tenant_id());
        """)

        # Policy de DELETE: só pode deletar dados do seu tenant
        op.execute(f"""
        CREATE POLICY {table_name}_tenant_isolation_delete ON {table_name}
        FOR DELETE
        USING (tenant_id = get_current_tenant_id());
        """)

    # RLS na tabela tenants: cada usuário só vê seu próprio tenant
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;")

    # Para tenants, precisamos de uma abordagem diferente
    # um usuário só pode ver o tenant que ele pertence
    op.execute("""
    CREATE POLICY tenants_isolation_select ON tenants
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.tenant_id = tenants.id
            AND users.id::text = COALESCE(current_setting('app.current_user_id', true), '')
        )
    );
    """)


def downgrade() -> None:
    # Remover RLS policies
    tables_with_rls = [
        "users",
        "accounts",
        "transactions",
        "categories",
        "recurrences",
        "webhook_logs",
    ]

    for table_name in tables_with_rls:
        op.execute(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;")
        op.execute(f"DROP POLICY IF EXISTS {table_name}_tenant_isolation_select ON {table_name};")
        op.execute(f"DROP POLICY IF EXISTS {table_name}_tenant_isolation_insert ON {table_name};")
        op.execute(f"DROP POLICY IF EXISTS {table_name}_tenant_isolation_update ON {table_name};")
        op.execute(f"DROP POLICY IF EXISTS {table_name}_tenant_isolation_delete ON {table_name};")

    # Remover RLS na tabela tenants
    op.execute("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY;")
    op.execute("DROP POLICY IF EXISTS tenants_isolation_select ON tenants;")

    # Remover função helper
    op.execute("DROP FUNCTION IF EXISTS get_current_tenant_id();")
