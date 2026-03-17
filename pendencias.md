# Pendencias - FinControl

**Data:** 17 de marco de 2026
**Status:** Em desenvolvimento acelerado
**Versao:** 0.1.0
**Ultima atualizacao:** 17 de marco de 2026 - BE-15, FE-16, MT-09 completados

---

## Resumo Executivo

### Status Geral: 11/12 gaps completados (92%)

```
COMPLETO (11): Gap #1, #2, #3, #4, #5, #6, #7, #8, #10, #11, #12
PENDENTE (1):  Gap #9 (Terraform IaC)
EM ABERTO:     BE-16 (AI Assistant) + Infra de producao
```

---

## Gaps Completados

| Gap | Titulo | Status | Data |
|-----|--------|--------|------|
| 1 | Testes de Integracao | COMPLETO | 17 mar |
| 2 | Frontend API Integration | COMPLETO | 16 mar |
| 3 | Multi-tenant RLS Security | COMPLETO | 16 mar |
| 4 | Middleware de Autenticacao | COMPLETO | 17 mar |
| 5 | Webhooks Open Finance | COMPLETO | 17 mar |
| 6 | Celery Beat Jobs | COMPLETO | 17 mar |
| 7 | Stripe Billing | COMPLETO | 17 mar |
| 8 | CI/CD Pipeline | COMPLETO | 17 mar |
| 10 | Frontend Pages (17 paginas) | COMPLETO | 17 mar |
| 11 | Plan Guard | COMPLETO | 17 mar |
| 12 | Conftest e Setup de Testes | COMPLETO | 17 mar |
| - | README profissional | COMPLETO | 16 mar |
| - | Rename: Visor -> FinControl | COMPLETO | 16 mar |
| - | BE-15: Email Service (SendGrid) | COMPLETO | 17 mar |
| - | FE-16: Onboarding | COMPLETO | 17 mar |
| - | MT-09: Admin Panel | COMPLETO | 17 mar |

### Implementados em 17 mar (sessao 2)

**BE-15 - Email Service (SendGrid):**
- `backend/app/services/email_service.py` - Servico completo com 5 templates:
  - `send_email()` - envio generico
  - `send_welcome()` - boas-vindas apos registro
  - `send_password_reset()` - recuperacao de senha
  - `send_plan_upgrade()` - confirmacao de upgrade
  - `send_sync_error()` - erro de sincronizacao bancaria
- `backend/app/workers/tasks.py` - 4 Celery tasks de email (welcome, notification, plan_upgrade, sync_error)
- `backend/app/api/v1/notifications.py` - Endpoints POST /notifications/send-test e /resend-welcome
- Integrado no fluxo de registro (envia welcome email via Celery)
- Testes em `backend/tests/test_email_service.py` (5 testes)

**FE-16 - Onboarding:**
- `frontend/src/app/(dashboard)/onboarding/page.tsx` - Fluxo de 4 etapas:
  - Step 0: Boas-vindas personalizado com nome do usuario
  - Step 1: Cadastro da primeira conta bancaria
  - Step 2: Selecao de objetivos financeiros
  - Step 3: Tela de conclusao com redirecionamento
- Registro agora redireciona para `/onboarding` ao inves de `/dashboard`
- Barra de progresso visual entre steps

**MT-09 - Admin Panel:**
- `backend/app/api/v1/admin.py` - 6 endpoints protegidos por `require_admin`:
  - GET /admin/stats - Estatisticas globais (tenants, users, accounts, transactions)
  - GET /admin/tenants - Listagem com paginacao e filtro por plano
  - PATCH /admin/tenants/{id} - Alterar plano/status
  - GET /admin/users - Listagem com paginacao e filtro
  - PATCH /admin/users/{id} - Ativar/desativar/verificar
  - GET /admin/webhook-logs - Logs de webhooks
- Controle de acesso via `ADMIN_EMAILS` (env var, comma-separated)
- `frontend/src/app/(dashboard)/admin/page.tsx` - Dashboard admin com:
  - Cards de estatisticas (tenants, users, accounts, transactions)
  - Distribuicao por plano (FREE/PRO/PREMIUM)
  - Tabela de tenants com edicao de plano inline
  - Tabela de usuarios com ativacao/desativacao
  - Tela de acesso negado para nao-admins
- Link "Admin" adicionado ao sidebar
- Testes em `backend/tests/test_admin.py` (7 testes)

---

## Gaps Pendentes

### 9. **Infrastructure as Code (IaC)**
- **Status:** Nao existe
- **Impacto:** Medio (deploy em producao)
- **Descricao:** Terraform para provisionar infra (DB, Redis, App)
- **O que falta:**
  - Terraform modules (networking, database, app)
  - Variaveis de ambiente por stage
  - Auto-scaling configs
  - Backup policies
  - Monitoring setup
  - Documentacao de deploy
- **Prioridade:** MEDIA

---

## Tarefas Adicionais Pendentes

### Backend
- **BE-16: AI Assistant** - Nao implementado

### Infraestrutura de Producao
- SRV-03: Terraform IaC (= Gap #9)
- SRV-04: PostgreSQL gerenciado + backups
- SRV-06: Nginx reverse proxy
- SRV-07: SSL (Let's Encrypt / Cloudflare)
- SRV-08: Rate limiting (nginx limit_req_zone)
- SRV-09: S3/R2 para exports
- SRV-10: Sentry + logs estruturados
- SRV-11: Secrets manager
- SRV-12: Autoscaling

---

## Arquitetura Atual (Implementada)

### Backend (15/16 tasks completos)
- FastAPI + SQLAlchemy 2.0 async + Alembic
- Celery + Redis (workers + beat scheduler)
- JWT auth + refresh tokens + TenantContextMiddleware
- Pluggy Open Finance: client, service, sync, webhooks
- Stripe: checkout, portal, subscription, webhooks
- SendGrid: email service com 5 templates + Celery tasks
- Admin Panel: stats, tenants, users, webhook-logs (RBAC por ADMIN_EMAILS)
- APIs: dashboard, contas, transacoes, categorias, recorrencias, faturas, projecoes, patrimonio, notificacoes, admin
- Plan Guard: limites por plano (FREE/PRO/PREMIUM)
- Auto-categorizacao: 71 regras para merchants BR
- Testes: 30+ testes com SQLite in-memory

### Frontend (17/17 pages completas)
- Next.js App Router + Tailwind + shadcn/ui
- React Query hooks para toda API
- Recharts para visualizacoes
- 17 paginas: login, register, onboarding, dashboard, transactions, accounts, cash-flow, categories, goals, invoices, net-worth, plans, projection, recurring, reports, admin + layouts

### Infra (3/12 tasks completos)
- Docker + docker-compose
- CI/CD (.github/workflows/ci.yml)
- Redis configurado

---

## Plano Recomendado (Proximos Passos)

### FASE 1 - Producao Minima (Prioridade)
1. Gap #9 - Terraform IaC
2. SRV-04 - PostgreSQL gerenciado
3. SRV-06/07 - Nginx + SSL
4. SRV-10 - Sentry + logs

### FASE 2 - Hardening
5. SRV-08 - Rate limiting
6. SRV-11 - Secrets manager

### FASE 3 - Features Extras
7. BE-16 - AI assistant
8. SRV-09 - S3/R2 exports
9. SRV-12 - Autoscaling

---

**Proxima atualizacao:** Apos deploy em staging
**Ultima atualizacao:** 17 de marco de 2026
