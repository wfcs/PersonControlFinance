# Multi-Tenant RLS Security Documentation

## Visão Geral

Este aplicativo implementa segurança multi-tenant em **3 camadas**:

### 1. **Row-Level Security (RLS) - PostgreSQL**
- Políticas automáticas de isolamento no banco de dados
- Cada query é filtrada pelo `tenant_id` automaticamente
- Previne vazamento de dados por bugs de aplicação

### 2. **Tenant Context - Application Layer**
- Context variables Python para rastrear `tenant_id` por request
- Session variables PostgreSQL para RLS funcionar
- Automático via middleware

### 3. **Decorators & Validação - Endpoint Layer**
- Validação explícita em endpoints sensíveis
- Previne acesso cross-tenant

---

## Como Funciona

### Request Flow

```
1. Cliente envia: GET /api/v1/categories
   Authorization: Bearer <JWT_TOKEN>

2. TenantContextMiddleware extrai token
   ↓
3. Decodifica JWT e extrai: tenant_id, user_id
   ↓
4. Executa: apply_tenant_context(session, tenant_id, user_id)
   ├─ set_current_tenant_id(tenant_id) [ContextVar]
   └─ SET app.current_tenant_id = '...' [PostgreSQL session var]
   ↓
5. Endpoint executa endpoint handler
   ↓
6. SELECT * FROM categories
   ├─ RLS Policy aplicada automaticamente
   └─ WHERE tenant_id = get_current_tenant_id() (função PostgreSQL)
   ↓
7. Retorna APENAS categorias do tenant_id do usuário
   ↓
8. clear_tenant_context() remove session vars após response
```

### RLS Policies

Cada tabela tenant-aware tem 4 políticas:

```sql
-- SELECT: Usuário vê apenas dados do seu tenant
CREATE POLICY categories_tenant_isolation_select ON categories
FOR SELECT
USING (tenant_id = get_current_tenant_id());

-- INSERT: Dados devem pertencer ao tenant do usuário
CREATE POLICY categories_tenant_isolation_insert ON categories
FOR INSERT
WITH CHECK (tenant_id = get_current_tenant_id());

-- UPDATE: Só atualiza dados do seu tenant
CREATE POLICY categories_tenant_isolation_update ON categories
FOR UPDATE
USING (tenant_id = get_current_tenant_id())
WITH CHECK (tenant_id = get_current_tenant_id());

-- DELETE: Só deleta dados do seu tenant
CREATE POLICY categories_tenant_isolation_delete ON categories
FOR DELETE
USING (tenant_id = get_current_tenant_id());
```

---

## Implementação em Endpoints

### ✅ Correto: Usar `current_user.tenant_id`

```python
from app.core.deps import AuthUser, DBSession
from app.core.tenant_decorators import require_tenant_context

@app.post("/categories")
@require_tenant_context  # Valida que contexto foi carregado
async def create_category(
    data: CategoryCreate,
    current_user: AuthUser,  # Já extrai tenant_id do JWT
    db: DBSession,
) -> CategoryOut:
    # Middleware já aplicou RLS para este tenant
    # Passar tenant_id do usuário é redundante (mas explícito)
    category = await category_service.create_category(
        data=data,
        tenant_id=current_user.tenant_id,  # De preference, use isto
        db=db,
    )
    return CategoryOut.model_validate(category)
```

### ❌ Errado: Query sem RLS

```python
# Sem aplicar tenant context, RLS não funciona!
async def get_all_categories():  # ❌ Sem current_user
    # SELECT * FROM categories (sem RLS)
    # Retorna TUDO se RLS não estiver ativado
    return await db.execute(select(Category))
```

### ❌ Errado: Ignorar tenant do usuário

```python
async def get_user_data(
    user_id: UUID,  # ❌ Receber user_id como parâmetro é arriscado!
    current_user: AuthUser,
    db: DBSession,
):
    # Alguém poderia fazer GET /users/outro-user-id/data
    # Mesmo com RLS, se a query não filtrar por tenant, pode vazar
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == user_id)
    )
    return result  # ❌ Mas e se user_id for de outro tenant?
```

### ✅ Correto: Sempre usar tenant_id do usuário

```python
async def get_user_transactions(
    current_user: AuthUser,
    db: DBSession,
):
    # RLS já filtra por tenant_id automaticamente
    result = await db.execute(
        select(Transaction).where(
            Transaction.tenant_id == current_user.tenant_id
        )
    )
    return result
```

---

## Testes

Validar isolamento com:

```bash
pytest backend/tests/test_rls_isolation.py -v
```

### O que é testado:
- ✅ RLS bloqueia SELECT de outro tenant
- ✅ RLS bloqueia INSERT com tenant_id diferente
- ✅ Context variables mantêm isolamento
- ✅ Contas de tenant1 invisíveis para tenant2
- ✅ Operações sem contexto falham

---

## Boas Práticas

1. **Sempre use `current_user.tenant_id` em endpoints protegidos**
   ```python
   # ✅ Bom
   await service.create(data, current_user.tenant_id, db)
   
   # ❌ Ruim
   await service.create(data, request.tenant_id, db)
   ```

2. **Não confie em parâmetros de tenant_id da URL**
   ```python
   # ❌ Ruim
   @app.get("/tenants/{tenant_id}/data")
   
   # ✅ Use apenas parâmetros de recurso
   @app.get("/categories/{cat_id}")
   ```

3. **Sempre aplicar decorator `@require_tenant_context`**
   ```python
   @app.post("/accounts")
   @require_tenant_context  # Segura contra erros
   async def create_account(...):
       ...
   ```

4. **Teste isolamento regularmente**
   ```bash
   pytest backend/tests/test_rls_isolation.py
   ```

---

## Troubleshooting

### "ERROR: new row violates row-level security policy"

Significa que RLS está funcionando! O erro indica:
- Tentativa de INSERT/UPDATE com tenant_id diferente
- Ou contexto de tenant não foi aplicado

**Solução:**
```python
# Certifique-se que TenantContextMiddleware está ativado em main.py
app.add_middleware(TenantContextMiddleware)
```

### "SELECT retorna linhas de outros tenants"

RLS não está ativado no banco. Verificar:

```sql
-- Verificar se RLS está ativeado
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'categories';

-- rowsecurity deve ser 't' (true)
```

Se retornar 'f', ativar:
```sql
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
```

### "Context variable vazio"

TenantContextMiddleware não rodou. Verificar:
1. Está registrado em `main.py`?
2. Request tem header `Authorization: Bearer ...`?
3. Token é válido?

---

## Arquivos Relacionados

- `backend/app/core/tenant_context.py` - Context variables e helpers
- `backend/app/core/tenant_middleware.py` - Middleware TenantContextMiddleware
- `backend/app/core/tenant_decorators.py` - Decorators de validação
- `backend/app/main.py` - Registro do middleware
- `backend/migrations/versions/0003_rls_policies.py` - Criação de RLS policies
- `backend/tests/test_rls_isolation.py` - Testes de isolamento
