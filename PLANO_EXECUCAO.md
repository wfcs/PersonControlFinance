# Plano de Execucao — PersonControlFinance

> Atualizado em: 2026-03-19
> Total: 53 tasks | Concluidas: 38/53 (72%)

---

## Fase 1 — Fundacao (BE-01, BE-02, BE-03, FE-01, SRV-01) ✅
> Estrutura base do projeto. Sem isso, nada roda.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| BE-01  | Setup FastAPI                 | Python     | COMPLETO ✅ |
| BE-02  | Modelagem do banco de dados   | SQL        | COMPLETO ✅ |
| BE-03  | Autenticacao JWT              | Python     | COMPLETO ✅ |
| FE-01  | Setup Next.js + Tailwind      | TypeScript | COMPLETO ✅ |
| SRV-01 | Docker + docker-compose (dev) | Docker     | COMPLETO ✅ |

---

## Fase 2 — Multi-tenant Core (MT-01, MT-02, MT-03, MT-04) ✅
> Isolamento por tenant e sistema de planos.

| ID     | Task                              | Stack      | Status      |
|--------|-----------------------------------|------------|-------------|
| MT-01  | tenant_id + composite indexes     | SQL        | COMPLETO ✅ |
| MT-02  | Row-Level Security (RLS)          | PostgreSQL | COMPLETO ✅ |
| MT-03  | Middleware isolamento por request  | Python     | COMPLETO ✅ |
| MT-04  | Sistema de planos e limites       | Python     | COMPLETO ✅ |

**Detalhes:** Composite indexes (tenant_id, id) em 7 tabelas. RLS via migration PostgreSQL (skip SQLite). TenantContextMiddleware com ContextVar. Planos free/pro/premium com plan_guard (check_account_limit). 16 testes passando.

---

## Fase 3 — APIs Core (BE-05, BE-06, BE-12, BE-13) ✅
> CRUD principal + webhooks. BE-04 (Open Finance) movido para fase futura.

| ID     | Task                          | Stack  | Status      |
|--------|-------------------------------|--------|-------------|
| BE-04  | Integracao Open Finance       | Python | PENDENTE    |
| BE-05  | API de transacoes             | Python | COMPLETO ✅ |
| BE-06  | Engine de categorizacao       | Python | COMPLETO ✅ |
| BE-12  | API de categorias e metas     | Python | COMPLETO ✅ |
| BE-13  | Webhooks Open Finance         | Python | COMPLETO ✅ |

**Detalhes:** CRUD completo para Accounts (com plan limit check), Transactions (filtros: data, conta, categoria, tipo, valor, busca + paginacao), Categories (com subcategorias parent_id), Goals (com progresso e status). Webhook endpoint POST /webhooks/pluggy com log + dispatch Celery. 30 testes passando.

---

## Fase 4 — Frontend Pages (FE-02 a FE-16) ✅
> Layout, auth e todas as 16 telas do app.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| FE-02  | Layout base e sidebar         | TypeScript | COMPLETO ✅ |
| FE-03  | Tela de autenticacao          | TypeScript | COMPLETO ✅ |
| FE-04  | Dashboard — visao geral       | React      | COMPLETO ✅ |
| FE-05  | Tela de transacoes            | React      | COMPLETO ✅ |
| FE-06  | Tela de contas                | React      | COMPLETO ✅ |
| FE-07  | Tela de recorrentes           | React      | COMPLETO ✅ |
| FE-08  | Tela de fluxo de caixa        | React      | COMPLETO ✅ |
| FE-09  | Tela de faturas               | React      | COMPLETO ✅ |
| FE-10  | Tela de categorias            | React      | COMPLETO ✅ |
| FE-11  | Tela de metas financeiras     | React      | COMPLETO ✅ |
| FE-12  | Tela de projecao de saldo     | React      | COMPLETO ✅ |
| FE-13  | Tela de patrimonio            | React      | COMPLETO ✅ |
| FE-14  | Tela de relatorios            | React      | COMPLETO ✅ |
| FE-15  | Tela de planos e assinatura   | React      | COMPLETO ✅ |
| FE-16  | Onboarding e convites         | React      | COMPLETO ✅ |

**Detalhes:** 17 componentes shadcn/ui (@base-ui/react). 6 React Query hooks (auth, accounts, transactions, categories, goals, dashboard). Sidebar dark com 12 nav items + Lucide icons. Dashboard com Recharts (LineChart, PieChart). Todas as paginas com dialogs CRUD, filtros, empty states. Build Next.js 16 passando sem erros.

---

## Fase 5 — APIs Secundarias (BE-07, BE-08, BE-09, BE-10, BE-11, BE-14) ✅
> Recorrencias, fluxo de caixa, projecao, patrimonio, faturas, sync periodico.

| ID     | Task                          | Stack  | Status      |
|--------|-------------------------------|--------|-------------|
| BE-07  | Motor de recorrencias         | Python | COMPLETO ✅ |
| BE-08  | API de fluxo de caixa         | Python | COMPLETO ✅ |
| BE-09  | API de projecao de saldo      | Python | COMPLETO ✅ |
| BE-10  | API de patrimonio             | Python | COMPLETO ✅ |
| BE-11  | API de faturas de cartao      | Python | COMPLETO ✅ |
| BE-14  | Job de sincronizacao          | Python | COMPLETO ✅ |

**Detalhes:** Motor de recorrencias com CRUD + process_due (gera transacoes automaticas) + detect (identifica padroes em historico). Cash flow agrupa receita/despesa por mes. Projecao projeta saldo futuro com base em recorrencias ativas. Patrimonio calcula ativos - passivos por tipo de conta. Faturas de cartao com CRUD + filtros por conta/status. Celery Beat: process_recurrences (diario) + sync_open_finance (horario). python-dateutil para relativedelta. 43 testes passando.

---

## Fase 6 — Billing e Monetizacao (MT-05, MT-06, MT-07) ✅
> Stripe, webhooks de pagamento, portal de billing.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| MT-05  | Integracao Stripe (billing)   | Python     | COMPLETO ✅ |
| MT-06  | Webhook Stripe                | Python     | COMPLETO ✅ |
| MT-07  | Portal de billing no frontend | React      | COMPLETO ✅ |

**Detalhes:** Stripe Checkout (subscription mode) + Customer Portal. billing_service.py com create_checkout_session, create_portal_session, handle_webhook_event. Webhook processa customer.subscription.created/updated/deleted e checkout.session.completed, atualiza tenant.plan automaticamente. Frontend plans page conectada com useSubscriptionStatus, useCreateCheckout, useCreatePortal. Tenant model estendido com stripe_customer_id e stripe_subscription_id. 48 testes passando.

---

## Fase 7 — Infra e CI/CD (SRV-02 a SRV-05)
> Pipeline, banco gerenciado, Redis, infraestrutura cloud.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| SRV-02 | CI/CD pipeline (GitHub Actions)| YAML/GHA  | PENDENTE    |
| SRV-03 | Infraestrutura cloud (IaC)    | Terraform  | PENDENTE    |
| SRV-04 | Banco gerenciado + backups    | PostgreSQL | PENDENTE    |
| SRV-05 | Redis (cache + fila Celery)   | Redis      | PENDENTE    |

---

## Fase 8 — Seguranca e Hardening (SRV-06 a SRV-10, MT-08)
> Proxy, SSL, rate limiting, storage, monitoramento, auditoria.

| ID     | Task                          | Stack  | Status      |
|--------|-------------------------------|--------|-------------|
| SRV-06 | API Gateway / reverse proxy   | Nginx  | PENDENTE    |
| SRV-07 | SSL/TLS e dominio             | Infra  | PENDENTE    |
| SRV-08 | Rate limiting                 | Infra  | PENDENTE    |
| SRV-09 | Storage S3 para exports       | Infra  | PENDENTE    |
| SRV-10 | Monitoramento e alertas       | Python | PENDENTE    |
| MT-08  | Auditoria por tenant          | SQL    | PENDENTE    |

---

## Fase 9 — Extras e Polish (BE-15, BE-16, MT-09, SRV-11, SRV-12)
> Notificacoes, IA, admin panel, secrets, autoscaling.

| ID     | Task                          | Stack  | Status      |
|--------|-------------------------------|--------|-------------|
| BE-15  | Sistema de notificacoes       | Python | PENDENTE    |
| BE-16  | Assistente de IA (premium)    | Python | PENDENTE    |
| MT-09  | Admin panel interno           | Python | PENDENTE    |
| SRV-11 | Secrets manager               | Infra  | PENDENTE    |
| SRV-12 | Autoscaling e observabilidade | Infra  | PENDENTE    |

---

## Stack Tecnica

| Camada     | Tecnologia                                         |
|------------|-----------------------------------------------------|
| Backend    | Python 3.14 + FastAPI + SQLAlchemy 2.0 async + Celery |
| Frontend   | Next.js 16 (App Router) + React 19 + Tailwind CSS 4 + shadcn/ui (base-ui) |
| State      | Zustand 5 + React Query 5                           |
| Charts     | Recharts 3                                           |
| Banco      | PostgreSQL (Supabase/Neon) + Alembic                |
| Cache/Fila | Redis                                               |
| Auth       | JWT (access + refresh tokens) + bcrypt              |
| Payments   | Stripe Billing                                      |
| Open Finance | Pluggy SDK                                        |
| CI/CD      | GitHub Actions                                      |
| Infra      | Docker + docker-compose (dev) / Terraform (prod)    |
| Monitoring | Sentry + logs estruturados                          |

---

## Progresso por Area

| Area          | Concluidas | Total | %    |
|---------------|-----------|-------|------|
| Backend (BE)  | 10/16     | 16    | 63%  |
| Frontend (FE) | 16/16     | 16    | 100% |
| Multi-tenant  | 7/9       | 9     | 78%  |
| Servidor/Infra| 1/12      | 12    | 8%   |
| **TOTAL**     | **38/53** | **53**| **72%** |
