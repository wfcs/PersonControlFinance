# Plano de Execucao — PersonControlFinance

> Atualizado em: 2026-03-18
> Total: 53 tasks | Concluidas: 0/53 (0%)

---

## Fase 1 — Fundacao (BE-01, BE-02, BE-03, FE-01, SRV-01)
> Estrutura base do projeto. Sem isso, nada roda.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| BE-01  | Setup FastAPI                 | Python     | PENDENTE    |
| BE-02  | Modelagem do banco de dados   | SQL        | PENDENTE    |
| BE-03  | Autenticacao JWT              | Python     | PENDENTE    |
| FE-01  | Setup Next.js + Tailwind      | TypeScript | PENDENTE    |
| SRV-01 | Docker + docker-compose (dev) | Docker     | PENDENTE    |

---

## Fase 2 — Multi-tenant Core (MT-01, MT-02, MT-03, MT-04)
> Isolamento por tenant e sistema de planos. Precisa estar pronto antes das APIs de negocio.

| ID     | Task                              | Stack      | Status      |
|--------|-----------------------------------|------------|-------------|
| MT-01  | tenant_id em todas tabelas        | SQL        | PENDENTE    |
| MT-02  | Row-Level Security (RLS)          | PostgreSQL | PENDENTE    |
| MT-03  | Middleware isolamento por request | Python     | PENDENTE    |
| MT-04  | Sistema de planos e limites       | Python     | PENDENTE    |

---

## Fase 3 — APIs Core (BE-04, BE-05, BE-06, BE-12, BE-13)
> CRUD principal + integracao Open Finance.

| ID     | Task                          | Stack  | Status      |
|--------|-------------------------------|--------|-------------|
| BE-04  | Integracao Open Finance       | Python | PENDENTE    |
| BE-05  | API de transacoes             | Python | PENDENTE    |
| BE-06  | Engine de categorizacao       | Python | PENDENTE    |
| BE-12  | API de categorias e metas     | Python | PENDENTE    |
| BE-13  | Webhooks Open Finance         | Python | PENDENTE    |

---

## Fase 4 — Frontend Core (FE-02, FE-03, FE-04, FE-05, FE-06)
> Layout, auth e telas principais. Depende das APIs da Fase 3.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| FE-02  | Layout base e sidebar         | TypeScript | PENDENTE    |
| FE-03  | Tela de autenticacao          | TypeScript | PENDENTE    |
| FE-04  | Dashboard — visao geral       | React      | PENDENTE    |
| FE-05  | Tela de transacoes            | React      | PENDENTE    |
| FE-06  | Tela de contas (Open Finance) | React      | PENDENTE    |

---

## Fase 5 — APIs Secundarias (BE-07, BE-08, BE-09, BE-10, BE-11, BE-14)
> Recorrencias, fluxo de caixa, projecao, patrimonio, faturas, sync periodico.

| ID     | Task                          | Stack  | Status      |
|--------|-------------------------------|--------|-------------|
| BE-07  | Motor de recorrencias         | Python | PENDENTE    |
| BE-08  | API de fluxo de caixa         | Python | PENDENTE    |
| BE-09  | API de projecao de saldo      | Python | PENDENTE    |
| BE-10  | API de patrimonio             | Python | PENDENTE    |
| BE-11  | API de faturas de cartao      | Python | PENDENTE    |
| BE-14  | Job de sincronizacao          | Python | PENDENTE    |

---

## Fase 6 — Frontend Secundario (FE-07 a FE-14)
> Telas que consomem as APIs da Fase 5.

| ID     | Task                          | Stack | Status      |
|--------|-------------------------------|-------|-------------|
| FE-07  | Tela de recorrentes           | React | PENDENTE    |
| FE-08  | Tela de fluxo de caixa        | React | PENDENTE    |
| FE-09  | Tela de faturas               | React | PENDENTE    |
| FE-10  | Tela de categorias            | React | PENDENTE    |
| FE-11  | Tela de metas financeiras     | React | PENDENTE    |
| FE-12  | Tela de projecao de saldo     | React | PENDENTE    |
| FE-13  | Tela de patrimonio            | React | PENDENTE    |
| FE-14  | Tela de relatorios            | React | PENDENTE    |

---

## Fase 7 — Billing e Monetizacao (MT-05, MT-06, MT-07)
> Stripe, webhooks de pagamento, portal de billing.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| MT-05  | Integracao Stripe (billing)   | TypeScript | PENDENTE    |
| MT-06  | Webhook Stripe                | Python     | PENDENTE    |
| MT-07  | Portal de billing no frontend | React      | PENDENTE    |

---

## Fase 8 — Infra e CI/CD (SRV-02 a SRV-05)
> Pipeline, banco gerenciado, Redis, infraestrutura cloud.

| ID     | Task                          | Stack      | Status      |
|--------|-------------------------------|------------|-------------|
| SRV-02 | CI/CD pipeline (GitHub Actions)| YAML/GHA  | PENDENTE    |
| SRV-03 | Infraestrutura cloud (IaC)    | Terraform  | PENDENTE    |
| SRV-04 | Banco gerenciado + backups    | PostgreSQL | PENDENTE    |
| SRV-05 | Redis (cache + fila Celery)   | Redis      | PENDENTE    |

---

## Fase 9 — Seguranca e Hardening (SRV-06 a SRV-10, MT-08)
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

## Fase 10 — Extras e Polish (BE-15, BE-16, FE-15, FE-16, MT-09, SRV-11, SRV-12)
> Notificacoes, IA, onboarding, admin panel, secrets, autoscaling.

| ID     | Task                          | Stack  | Status      |
|--------|-------------------------------|--------|-------------|
| BE-15  | Sistema de notificacoes       | Python | PENDENTE    |
| BE-16  | Assistente de IA (premium)    | Python | PENDENTE    |
| FE-15  | Tela de planos e assinatura   | React  | PENDENTE    |
| FE-16  | Onboarding e convites         | React  | PENDENTE    |
| MT-09  | Admin panel interno           | Python | PENDENTE    |
| SRV-11 | Secrets manager               | Infra  | PENDENTE    |
| SRV-12 | Autoscaling e observabilidade | Infra  | PENDENTE    |

---

## Stack Tecnica

| Camada     | Tecnologia                                         |
|------------|-----------------------------------------------------|
| Backend    | Python 3.12 + FastAPI + SQLAlchemy 2.0 async + Celery |
| Frontend   | Next.js 15 (App Router) + React 19 + Tailwind CSS 4 + shadcn/ui |
| State      | Zustand 5 + React Query 5                           |
| Banco      | PostgreSQL (Supabase/Neon) + Alembic                |
| Cache/Fila | Redis                                               |
| Auth       | JWT (access + refresh tokens) + bcrypt              |
| Payments   | Stripe Billing                                      |
| Open Finance | Pluggy SDK                                        |
| CI/CD      | GitHub Actions                                      |
| Infra      | Docker + docker-compose (dev) / Terraform (prod)    |
| Monitoring | Sentry + logs estruturados                          |
