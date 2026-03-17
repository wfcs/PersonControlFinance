# 📋 Pendências - FinControl

**Data:** 16 de março de 2026  
**Status:** Em desenvolvimento acelerado  
**Versão:** 0.1.0  
**Última atualização:** 16 de março de 2026 - Gaps #2, #3, #10 completados

---

## 🚩 Gaps Pendentes (Prioridade Atual)

### 4. **Middleware de Autenticação Global**
- **Status:** ⏳ PRÓXIMO A IMPLEMENTAR
- **Impacto:** Alto
- **Descrição:** Endpoint que requerem auth devem validad tokens consistentemente em toda API
- **Arquivos envolvidos:**
  - `backend/app/core/security.py` - Lógica JWT (já existe)
  - `backend/app/core/deps.py` - Dependência AuthUser (já existe)
  - `backend/app/main.py` - App FastAPI (TenantContextMiddleware já integrado)
  - `backend/app/api/v1/` - Todos os endpoints
- **O que falta:**
  - ✗ Token expiration validation consistente
  - ✗ Logout com token blacklist (Redis)
  - ✗ CORS específico por ambiente
  - ✗ Rate limiting por usuário
  - ✗ Refresh token automático no frontend (já existe)
  - ✗ Testes de auth em endpoints
- **Arquivos já prontos para uso:**
  - ✅ TenantContextMiddleware (já injetado)
  - ✅ AuthUser dependency
  - ✅ JWT encode/decode
  - ✅ Refresh token flow
- **Prioridade:** 🔴 ALTA (RECOMENDADO PARA AMANHÃ)

---

### 1. **Testes de Integração dos Endpoints**
- **Status:** ⏳ BLOQUEADO (aguarda Gap #4)
- **Impacto:** Alto
- **Descrição:** Todos os endpoints precisam de testes de integração completos
- **Arquivos envolvidos:**
  - `backend/tests/conftest.py` - Fixtures (parcial)
  - `backend/tests/test_*.py` - Testes por endpoint
  - `backend/tests/test_rls_isolation.py` - ✅ Testes RLS já existem
- **O que falta:**
  - ✗ Fixtures para AsyncClient
  - ✗ Database de teste isolado
  - ✗ User/tenant factories
  - ✗ JWT token mocks
  - ✗ Testes de todos endpoints (POST, GET, PATCH, DELETE)
  - ✗ Testes de validação de planos
  - ✗ Edge cases e error handling
- **Prioridade:** 🔴 ALTA (DEPOIS DE #4)

---

### 7. **Integração Stripe (Billing)**
- **Status:** ⏳ AGUARDANDO
- **Impacto:** Alto (para monetização)
- **Descrição:** Checkout, webhooks e atualização de planos
- **Arquivos envolvidos:**
  - `backend/app/services/stripe_service.py` - ✅ Service existe
  - `backend/app/api/v1/billing.py` - Endpoints (vazio)
  - `backend/app/models/tenant.py` - ✅ Stripe IDs já existem
- **O que falta:**
  - ✗ Endpoint POST /api/v1/billing/checkout (criar session)
  - ✗ Endpoint POST /api/v1/billing/webhook (receber eventos)
  - ✗ Lógica de atualização de plano após pagamento
  - ✗ Sincronização de status com tenants
  - ✗ Testes de pagamento (mock Stripe)
  - ✗ Email de confirmação
  - ✗ Portal de gerenciamento do cliente
- **Prioridade:** 🔴 ALTA (NECESSÁRIO PARA PRODUÇÃO)

---

## 🟡 Gaps de Média Prioridade

### 5. **Webhooks Open Finance**
- **Status:** ⚠️ Estrutura pronta, não testada
- **Impacto:** Médio (sincronização em tempo real)
- **Descrição:** Processar eventos de contas abertas/fechadas do Open Finance
- **Arquivos envolvidos:**
  - `backend/app/api/v1/webhooks.py` - ✅ Endpoint existe
  - `backend/app/workers/tasks.py` - ✅ Tasks existem
  - `backend/app/services/pluggy_service.py` - ✅ Integração existe
- **O que falta:**
  - ✗ Validação de assinatura Pluggy
  - ✗ Retry automático em falhas
  - ✗ Logging estruturado
  - ✗ Testes end-to-end com Pluggy mock
  - ✗ Monitoramento de processamento
- **Prioridade:** 🟡 MÉDIA

---

### 6. **Job de Sincronização Periódica (Celery Beat)**
- **Status:** ❌ Não implementado
- **Impacto:** Médio (dados atualizados)
- **Descrição:** Sincronizar contas/transações periodicamente (mesmo sem webhooks)
- **Arquivos envolvidos:**
  - `backend/app/workers/celery_app.py` - ✅ Celery configurado
  - `backend/app/workers/tasks.py` - ✅ Tasks estruturadas
  - `docker-compose.yml` - ✅ Serviço beat existe
- **O que falta:**
  - ✗ Agendamento de tasks (a cada 1h, 6h, diariamente)
  - ✗ Tenants priorities
  - ✗ Error handling e retry
  - ✗ Logging de execução
  - ✗ Monitoramento de status
  - ✗ Tests de agendamento
- **Prioridade:** 🟡 MÉDIA

---

### 8. **CI/CD Pipeline**
- **Status:** ❌ Não existe
- **Impacto:** Médio (automação)
- **Descrição:** Executar testes, build, deploy automaticamente
- **Arquivos envolvidos:**
  - `.github/workflows/` - NÃO EXISTE
- **O que falta:**
  - ✗ Workflow: lint (ruff + black)
  - ✗ Workflow: tests (pytest com coverage)
  - ✗ Workflow: build Docker
  - ✗ Workflow: push para registry
  - ✗ Workflow: deploy em staging
  - ✗ Status badges no README
- **Prioridade:** 🟡 MÉDIA (importante para produção)

---

### 9. **Infrastructure as Code (IaC)**
- **Status:** ❌ Não existe
- **Impacto:** Médio (deploy em produção)
- **Descrição:** Terraform para provisionar infra (DB, Redis, App)
- **Arquivos envolvidos:**
  - `terraform/` - NÃO EXISTE
  - `docs/DEPLOY.md` - Documentação de deployment
- **O que falta:**
  - ✗ Terraform modules (networking, database, app)
  - ✗ Variáveis de ambiente por stage
  - ✗ Auto-scaling configs
  - ✗ Backup policies
  - ✗ Monitoring setup
  - ✗ Documentação de deploy
- **Prioridade:** 🟡 MÉDIA

---

### 11. **Plan Guard - Validação de Planos**
- **Status:** ⚠️ Arquivo criado, não integrado
- **Impacto:** Médio (necessário para billing)
- **Descrição:** Validar limites de recursos por plano em endpoints
- **Arquivos envolvidos:**
  - `backend/app/core/plan_guard.py` - ✅ Validator existe
  - `backend/app/core/plan_limits.py` - ✅ Limites definidos
  - Endpoints - SEM VALIDAÇÃO
- **O que falta:**
  - ✗ Decorator @check_plan_limit("resource", "limit_key")
  - ✗ Aplicação em endpoints críticos (accounts, connections)
  - ✗ Mensagens de erro claras (upgrade needed)
  - ✗ Testes de limite por plano
  - ✗ Dashboard de uso/limites para usuário
- **Prioridade:** 🟡 MÉDIA

---

### 12. **Conftest e Setup Completo de Testes**
- **Status:** ⚠️ Arquivo vazio
- **Impacto:** Médio (facilita testes)
- **Descrição:** Fixtures reutilizáveis para toda suíte de testes
- **Arquivos envolvidos:**
  - `backend/tests/conftest.py` - VAZIO
- **O que falta:**
  - ✗ @pytest.fixture async def db_session
  - ✗ @pytest.fixture async def client (AsyncClient)
  - ✗ @pytest.fixture async def user_factory
  - ✗ @pytest.fixture async def tenant_factory
  - ✗ @pytest.fixture def valid_jwt_token
  - ✗ Setup/teardown de DB de teste
  - ✗ Mocks para Pluggy, Stripe
- **Prioridade:** 🟡 MÉDIA

---

## 📊 Resumo Executivo

### Status Geral: 3/12 gaps completados (25%)

```
✅ COMPLETO (3):  Gap #2, #3, #10
🔴 ALTA (3):     Gap #1, #4, #7  
🟡 MÉDIA (5):    Gap #5, #6, #8, #9, #11, #12
⏳ BLOQUEADO:    Gap #1 (aguarda #4)
```

### Avanços Realizados (16 de mar 2026)

| Gap | Título | Status |
|-----|--------|--------|
| 2 | Frontend API Integration | ✅ COMPLETO |
| 3 | Multi-tenant RLS Security | ✅ COMPLETO |
| 10 | Frontend Pages (11 páginas) | ✅ COMPLETO |
| - | README profissional | ✅ COMPLETO |
| - | Rename: Visor → FinControl | ✅ COMPLETO |

---

## 🎯 Plano Recomendado

### FASE 1 - Segurança (Hoje + Amanhã)
1. ✅ Gap #3 - RLS Security - CONCLUÍDO
2. 🔴 Gap #4 - Auth Middleware - **COMEÇAR AMANHÃ**
3. 🔴 Gap #1 - Integration Tests (após #4)

### FASE 2 - Monetização (Próxima semana)
4. 🔴 Gap #7 - Stripe Billing
5. 🟡 Gap #11 - Plan Guard

### FASE 3 - Automação (Próxima semana)
6. 🟡 Gap #6 - Celery Beat Jobs
7. 🟡 Gap #5 - Open Finance Webhooks
8. 🟡 Gap #8 - CI/CD Pipeline

### FASE 4 - Infraestrutura (Futuro)
9. 🟡 Gap #9 - Terraform IaC

---

## ✨ Destaques da Semana

### Implementado (16 de mar):
- ✅ **11 Dashboard Pages** com Recharts visualizações
- ✅ **RLS Multi-tenant** com PostgreSQL + Middleware
- ✅ **React Query Hooks** para toda API (11 hooks personalizados)
- ✅ **JWT + Refresh Token** flow completo
- ✅ **README Profissional** (400+ linhas)
- ✅ **App Rename** Visor → FinControl

### Commits da Semana:
1. `4408a95` - Gap #2: Frontend API Integration
2. `8de4927` - Gap #10: Dashboard Pages (11 páginas)
3. `3a5375f` - Gap #3: Multi-tenant RLS Security
4. `35c9bc0` - README profissional
5. `6c69b16` - Rename Visor → FinControl

---

## 📝 Como Contribuir Amanhã

### Gap #4 - Middleware de Autenticação (PRÓXIMO)

```bash
# 1. Criar branch
git checkout -b gap/4-auth-middleware

# 2. Implementar:
# - Token expiration validation
# - Logout endpoint com Redis blacklist
# - Rate limiting decorator
# - CORS configurável

# 3. Testar
pytest backend/tests/test_auth_middleware.py -v

# 4. Commit
git commit -m "feat: Auth Middleware (Gap #4)"

# 5. Atualizar pendencias.md
```

### Checklist Pre-Implementation

- [ ] Ler este arquivo
- [ ] Verificar `backend/app/core/security.py`
- [ ] Entender TenantContextMiddleware pattern
- [ ] Revisar tests em `backend/tests/test_auth.py`
- [ ] Criar fixtures em conftest.py se necessário

---

**Próxima atualização:** Após completar Gap #4  
**Estimativa:** 17 de março de 2026

---

**Última atualização:** 16 de março de 2026
