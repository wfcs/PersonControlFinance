# 📋 Pendências - App Fin

**Data:** 16 de março de 2026  
**Status:** Em desenvolvimento  
**Versão:** 0.1.0

---

## 🚩 Gaps Críticos

### 1. **Testes de Integração dos Endpoints**
- **Status:** ❌ Não implementado
- **Impacto:** Alto
- **Descrição:** Os endpoints da API estão criados mas não têm testes de integração reais
- **Arquivos envolvidos:**
  - `backend/tests/conftest.py` - Fixtures necessárias
  - `backend/tests/test_*.py` - Todos os testes
- **O que falta:**
  - ✗ Setup de database de teste
  - ✗ Fixtures para usuários/tenants
  - ✗ Mock de Open Finance
  - ✗ Validação de respostas HTTP
  - ✗ Testes de autenticação JWT
- **Prioridade:** 🔴 ALTA

---

### 2. **Frontend Desconectado da API**
- **Status:** ✅ IMPLEMENTADO
- **Impacto:** Alto
- **Descrição:** Componentes e hooks agora estão completamente conectados à API
- **Arquivos envolvidos:**
  - `frontend/src/lib/api.ts` - ✅ Axios instance com interceptadores
  - `frontend/src/lib/auth.ts` - ✅ Métodos de autenticação
  - `frontend/src/hooks/*.ts` - ✅ Todos os hooks com chamadas HTTP
  - `frontend/src/stores/auth-store.ts` - ✅ Store Zustand completo
  - `frontend/.env.example` - ✅ Documentação de variáveis
- **O que foi implementado:**
  - ✅ Endpoints configurados no `api.ts` com interceptadores
  - ✅ React Query hooks para autenticação, contas, transações, categorias, etc
  - ✅ Tratamento de erros HTTP com fallback
  - ✅ Auth token nos headers automaticamente
  - ✅ Refresh token flow com retry queue
  - ✅ Hooks adicionais: use-categories, use-patrimony, use-projections, use-recurrences, use-bills, use-open-finance
  - ✅ Documentação completa em HOOKS_DOCUMENTATION.md
  - ✅ Logout com invalidação de cache
- **Prioridade:** 🔴 ALTA → ✅ COMPLETO

---

### 3. **Segurança Multi-tenant**
- **Status:** ⚠️ Parcialmente implementado
- **Impacto:** Alto
- **Descrição:** tenant_id está nos modelos mas Row-Level Security (RLS) não foi aplicado
- **Arquivos envolvidos:**
  - `backend/app/models/base.py` - TenantMixin criado
  - `backend/app/core/deps.py` - Dependência de tenant
  - Migrations do PostgreSQL
- **O que falta:**
  - ✗ RLS policies no PostgreSQL
  - ✗ Validação de isolamento em testes
  - ✗ Middleware que injeta tenant_id em TODA request
  - ✗ Bloqueio de acesso cross-tenant
  - ✗ Row-level filtering automático
- **Prioridade:** 🔴 ALTA

---

### 4. **Middleware de Autenticação**
- **Status:** ⚠️ Parcialmente implementado
- **Impacto:** Alto
- **Descrição:** JWT básico existe mas não está aplicado consistentemente
- **Arquivos envolvidos:**
  - `backend/app/core/security.py` - Lógica JWT
  - `backend/app/core/deps.py` - Dependência AuthUser
  - `backend/app/main.py` - App FastAPI
- **O que falta:**
  - ✗ Middleware global que valida token em toda request
  - ✗ Refresh token automático
  - ✗ Logout (token blacklist)
  - ✗ CORS específico por ambiente
  - ✗ Rate limiting por usuário
- **Prioridade:** 🔴 ALTA

---

### 5. **Webhooks Open Finance**
- **Status:** ⚠️ Estrutura existe, processamento não validado
- **Impacto:** Médio
- **Descrição:** Endpoint de webhook existe mas não foi testado de ponta a ponta
- **Arquivos envolvidos:**
  - `backend/app/api/v1/webhooks.py` - Endpoint webhook
  - `backend/app/workers/tasks.py` - Tasks Celery
  - `backend/app/services/pluggy_service.py` - Lógica Pluggy
- **O que falta:**
  - ✗ Validação de assinatura do webhook
  - ✗ Testes de processamento assíncrono
  - ✗ Retry logic para falhas
  - ✗ Logging estruturado
  - ✗ Teste com Pluggy mock
- **Prioridade:** 🟡 MÉDIA

---

### 6. **Job de Sincronização Periódica (Celery Beat)**
- **Status:** ❌ Não implementado
- **Impacto:** Médio
- **Descrição:** Celery Beat configurado mas não há tasks agendadas
- **Arquivos envolvidos:**
  - `backend/app/workers/celery_app.py` - Config Celery
  - `backend/app/workers/tasks.py` - Tasks
  - `docker-compose.yml` - Serviço Beat
- **O que falta:**
  - ✗ Tasks de sync Open Finance por tenant
  - ✗ Schedule configuration
  - ✗ Retry policies
  - ✗ Monitoramento de falhas
  - ✗ Testes de agendamento
- **Prioridade:** 🟡 MÉDIA

---

### 7. **Integração Stripe (Billing)**
- **Status:** ⚠️ Service criado, endpoints faltam
- **Impacto:** Alto
- **Descrição:** Logic Stripe existe mas endpoints de checkout não implementados
- **Arquivos envolvidos:**
  - `backend/app/services/stripe_service.py` - Service
  - `backend/app/api/v1/billing.py` - Endpoint
- **O que falta:**
  - ✗ Endpoint de checkout
  - ✗ Webhook Stripe processing
  - ✗ Update de plan status
  - ✗ Integração com sistema de planos
  - ✗ Tests de billing
- **Prioridade:** 🔴 ALTA

---

### 8. **CI/CD Pipeline**
- **Status:** ❌ Completamente ausente
- **Impacto:** Médio
- **Descrição:** Nenhuma automação de build/test/deploy
- **Arquivos envolvidos:**
  - `.github/workflows/` - Não existe
- **O que falta:**
  - ✗ GitHub Actions workflow
  - ✗ Lint (ruff) automático
  - ✗ Tests automáticos (pytest)
  - ✗ Build Docker image
  - ✗ Deploy automático
- **Prioridade:** 🟡 MÉDIA

---

### 9. **Infrastructure as Code (IaC)**
- **Status:** ❌ Completamente ausente
- **Impacto:** Médio
- **Descrição:** Nenhuma automação de infraestrutura
- **Arquivos envolvidos:**
  - `terraform/` - Não existe
  - `.env.example` - Não existe
- **O que falta:**
  - ✗ Terraform code (PostgreSQL, Redis, App Services)
  - ✗ Environment variables documentation
  - ✗ Networking config
  - ✗ SSL/TLS setup
  - ✗ Backups automáticos
- **Prioridade:** 🟡 MÉDIA

---

### 10. **Frontend - Páginas Funcionais**
- **Status:** ❌ Estrutura apenas
- **Impacto:** Alto
- **Descrição:** Componentes shadcn importados mas páginas vazias
- **Arquivos envolvidos:**
  - `frontend/src/app/(dashboard)/` - Páginas vazias
  - `frontend/src/components/` - Components incompletos
- **O que falta:**
  - ✗ Dashboard com gráficos (Recharts integrado)
  - ✗ Tabela de transações
  - ✗ Formulários de categoria
  - ✗ Tela de contas (Open Finance)
  - ✗ Gráficos de fluxo de caixa
- **Prioridade:** 🔴 ALTA

---

### 11. **Validação de Planos (Plan Guard)**
- **Status:** ⚠️ Arquivo criado, lógica não aplicada
- **Impacto:** Médio
- **Descrição:** plan_guard.py e plan_limits.py existem mas não estão sendo usados
- **Arquivos envolvidos:**
  - `backend/app/core/plan_guard.py` - Validator
  - `backend/app/core/plan_limits.py` - Limites
  - Endpoints da API - Não validam plano
- **O que falta:**
  - ✗ Decorator de verificação de plano
  - ✗ Aplicação em endpoints
  - ✗ Testes de limite de conexões
  - ✗ Testes de recursos premium
- **Prioridade:** 🟡 MÉDIA

---

### 12. **Conftest e Setup de Testes**
- **Status:** ⚠️ Arquivo vazio
- **Impacto:** Médio
- **Descrição:** conftest.py existe mas sem implementação
- **Arquivos envolvidos:**
  - `backend/tests/conftest.py` - Fixtures
- **O que falta:**
  - ✗ Database de teste fixture
  - ✗ AsyncClient fixture
  - ✗ User/tenant fixtures
  - ✗ JWT token fixtures
  - ✗ Mock de Pluggy
- **Prioridade:** 🟡 MÉDIA

---

## 📊 Resumo por Prioridade

### 🔴 ALTA (7 itens)
1. Testes de Integração dos Endpoints
2. Frontend Desconectado da API
3. Segurança Multi-tenant (RLS)
4. Middleware de Autenticação
7. Integração Stripe (Billing)
10. Frontend - Páginas Funcionais

### 🟡 MÉDIA (5 itens)
5. Webhooks Open Finance
6. Job de Sincronização Periódica
8. CI/CD Pipeline
9. Infrastructure as Code
11. Validação de Planos

---

## 🎯 Próximos Passos Recomendados

1. **Fase 1 - Segurança & Autenticação** (Semana 1)
   - Setup `conftest.py` com fixtures
   - Middleware de autenticação + RLS
   - Testes de integração básicos

2. **Fase 2 - API & Frontend** (Semana 2-3)
   - Executar testes dos endpoints
   - Conectar frontend à API
   - Implementar páginas principais

3. **Fase 3 - Features** (Semana 4)
   - Webhooks de Open Finance
   - Stripe integration
   - Celery Beat jobs

4. **Fase 4 - DevOps** (Semana 5)
   - CI/CD pipeline
   - IaC (Terraform)
   - Monitoramento

---

## 📝 Template para Revisão

Antes de iniciar trabalho em qualquer gap:
- [ ] Ler este arquivo
- [ ] Revisar os arquivos envolvidos
- [ ] Criar branch feature: `git checkout -b gap/<nome>`
- [ ] Implementar e testar
- [ ] Atualizar este arquivo (marcar como ✅)
- [ ] Pull request para revisão

---

**Última atualização:** 16 de março de 2026
