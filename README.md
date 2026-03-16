# Visor — Controle Financeiro Pessoal

SaaS de controle financeiro para pessoa física conectado via Open Finance (Pluggy).

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Back-end | Python 3.11 + FastAPI + SQLAlchemy 2.0 async |
| Banco | PostgreSQL (Supabase) + Alembic |
| Cache / Fila | Redis + Celery |
| Front-end | Next.js 14 (App Router) + TypeScript + Tailwind |
| Auth | JWT (access + refresh) |
| Open Finance | Pluggy API |
| Billing | Stripe |
| CI/CD | GitHub Actions |

## Estrutura do Monorepo

```
visor/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # Routers FastAPI
│   │   ├── core/          # Config, segurança, deps
│   │   ├── db/            # Session async
│   │   ├── models/        # SQLAlchemy ORM
│   │   ├── schemas/       # Pydantic I/O
│   │   ├── services/      # Lógica de negócio
│   │   └── workers/       # Celery tasks
│   ├── migrations/        # Alembic
│   └── tests/
├── frontend/              # Next.js (em breve)
├── docker-compose.yml
└── .github/workflows/
```

## Rodando localmente

### 1. Clone e configure

```bash
git clone https://github.com/seu-user/visor.git
cd visor
cp .env.example .env
# Preencha as variáveis no .env
```

### 2. Suba os serviços

```bash
docker-compose up -d
```

A API estará disponível em `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

### 3. Rode as migrations

```bash
cd backend
alembic upgrade head
```

### 4. Testes

```bash
cd backend
pip install -e ".[dev]" aiosqlite
pytest tests/ -v
```

## Endpoints principais

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | Cadastro |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Renovar token |
| GET | `/api/v1/auth/me` | Usuário atual |
| GET | `/api/v1/accounts/` | Listar contas |
| POST | `/api/v1/accounts/` | Criar conta |
| GET | `/api/v1/transactions/` | Listar transações |
| POST | `/api/v1/transactions/` | Criar transação |
| GET | `/api/v1/transactions/summary` | Resumo mensal |
| GET | `/api/v1/transactions/by-category` | Gastos por categoria |
| GET | `/api/v1/transactions/export/csv` | Export CSV |

## Planos

| | Free | Pro | Premium |
|---|---|---|---|
| Conexões Open Finance | 1 | 3 | Ilimitadas |
| Preço | — | R$ 29/mês | R$ 49,75/mês |
| Contas PJ | ✗ | ✗ | ✓ |
| Assistente IA | ✗ | ✗ | ✓ |

## Próximos passos

- [ ] FE-01 a FE-04: Setup Next.js + dashboard
- [ ] BE-04: Integração Pluggy (Open Finance)
- [ ] MT-01 a MT-03: Hardening multi-tenant + RLS
- [ ] BE-07: Motor de detecção de recorrências
- [ ] MT-05: Integração Stripe
