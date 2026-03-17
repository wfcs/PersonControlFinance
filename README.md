# Visor - Controle Financeiro Pessoal com Open Finance

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-latest-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-in_development-yellow.svg)

**Visor** é uma aplicação web de código aberto para controle financeiro pessoal que integra com **Open Finance (Brasil)** via Pluggy. Oferece visibilidade completa sobre suas finanças com dashboards inteligentes, análises preditivas e detecção automática de padrões de gastos.

> 🚀 **Status:** Em desenvolvimento ativo | **Última atualização:** Março 2026

---

## 📋 Sumário

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Arquitetura](#-arquitetura)
- [Início Rápido](#-início-rápido)
- [Documentação](#-documentação)
- [Status do Projeto](#-status-do-projeto)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

---

## ✨ Features

### 💳 Integração Open Finance
- ✅ Conexão segura com múltiplas instituições via Pluggy
- ✅ Sincronização automática de contas e transações
- ✅ Suporte a contas correntes, poupança, cartões e investimentos
- ✅ Webhooks para atualização em tempo real

### 📊 Dashboards & Visualizações
- ✅ Dashboard principal com KPIs (receita, despesa, resultado)
- ✅ Gráficos de fluxo de caixa (12 meses)
- ✅ Análise de gastos por categoria
- ✅ Projeção de saldo futuro com alertas
- ✅ Evolução do patrimônio líquido
- ✅ Relatórios exportáveis

### 🤖 Inteligência & Automação
- ✅ Detecção automática de despesas recorrentes
- ✅ Categorização inteligente de transações
- ✅ Análise preditiva de saldo futuro
- ✅ Limites de orçamento por categoria
- ✅ Alertas de gastos excessivos

### 🔐 Segurança & Multi-tenant
- ✅ Isolamento multi-tenant com RLS (Row-Level Security)
- ✅ Autenticação JWT com refresh token automático
- ✅ Proteção contra CSRF e SQL injection
- ✅ CORS configurável por ambiente

### 💰 Planos & Monetização
- ✅ Modelo freemium (Basic, Pro, Premium)
- ✅ Integração com Stripe para pagamentos
- ✅ Validação de limites por plano
- ✅ Upgrade/downgrade automático

### 📱 Frontend Responsivo
- ✅ Design mobile-first com Tailwind CSS
- ✅ 11 páginas do dashboard implementadas
- ✅ Interface intuitiva com shadcn/ui
- ✅ Performance otimizada

---

## 🛠 Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL 14+ |
| **Auth** | JWT + Refresh Token |
| **Cache/Queue** | Redis + Celery |
| **Validation** | Pydantic v2 |

### Frontend
| Component | Technology |
|-----------|-----------|
| **Framework** | Next.js 16 |
| **Runtime** | React 19 |
| **Language** | TypeScript |
| **State** | React Query + Zustand |
| **Styling** | Tailwind CSS + shadcn/ui |
| **Forms** | React Hook Form + Zod |
| **Charts** | Recharts 3.8+ |

### DevOps
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions (em progresso)
- **IaC:** Terraform (em progresso)

---

## 🏗 Arquitetura

### Visão Geral

```
┌─────────────────────────┐
│   Browser (Cliente)     │
└────────┬────────────────┘
         │ HTTPS
┌────────▼──────────────────────────────────────┐
│   Frontend (Next.js + React)                  │
│   - 11 páginas de dashboard                   │
│   - React Query + Zustand                     │
│   - Axios com interceptors (JWT, refresh)     │
└─────────────────┬──────────────────────────────┘
                  │ REST API
┌─────────────────▼──────────────────────────────┐
│   Backend API (FastAPI)                        │
│   - TenantContextMiddleware (RLS)             │
│   - Routes (Auth, Accounts, Transactions)     │
│   - Services (Business Logic)                 │
│   - SQLAlchemy ORM + RLS Policies             │
│   - Celery + Redis (Async Jobs)               │
└─────────────────┬──────────────────────────────┘
        ┌────────┼────────┬────────┐
        │        │        │        │
        ▼        ▼        ▼        ▼
    PostgreSQL  Redis   Pluggy   Stripe
    (Primary)  (Cache) (Open    (Payments)
               (Queue)  Finance)
```

---

## 🚀 Início Rápido

### Pré-requisitos
- **Python** 3.12+
- **Node.js** 18+
- **Docker** + **Docker Compose**
- **PostgreSQL** 14+ (ou via Docker)
- **Redis** (ou via Docker)

### Com Docker (Recomendado)

```bash
# Clone
git clone https://github.com/wfcs/financial_application.git
cd financial_application

# Configure variáveis de ambiente
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Inicie serviços
docker-compose up -d

# Execute migrations
docker-compose exec backend alembic upgrade head
```

Acesse:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432

### Setup Local

#### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate

pip install -r pyproject.toml
cp .env.example .env

alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Configure: NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

---

## 📖 Documentação

### Documentos Principais
- [MULTITENANT_RLS.md](./backend/MULTITENANT_RLS.md) - Segurança multi-tenant
- [HOOKS_DOCUMENTATION.md](./frontend/HOOKS_DOCUMENTATION.md) - React Query hooks
- [SETP_MULTITENANT_EXAMPLE.py](./backend/SETP_MULTITENANT_EXAMPLE.py) - Exemplos de endpoints

### Endpoints Principais

**Autenticação**
```bash
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

**Contas**
```bash
GET    /api/v1/accounts
POST   /api/v1/accounts
GET    /api/v1/accounts/{id}
PATCH  /api/v1/accounts/{id}
DELETE /api/v1/accounts/{id}
```

**Transações**
```bash
GET    /api/v1/transactions
POST   /api/v1/transactions
GET    /api/v1/transactions/{id}
PATCH  /api/v1/transactions/{id}
DELETE /api/v1/transactions/{id}
```

---

## 📊 Status do Projeto

### Gaps Implementados (3/13)

| # | Gap | Status |
|---|-----|--------|
| 2 | Frontend API Integration | ✅ |
| 3 | Multi-tenant RLS Security | ✅ |
| 10 | Frontend Pages | ✅ |

### Próximos Passos (High Priority)

| # | Gap | Status |
|---|-----|--------|
| 1 | Integration Tests | ⏳ |
| 4 | Auth Middleware | ⏳ |
| 7 | Stripe Integration | ⏳ |

Veja [pendencias.md](./pendencias.md) para lista completa.

---

## 🧪 Testes

```bash
# Backend
cd backend
pytest tests/ -v

# Com coverage
pytest tests/ --cov=app --cov-report=html

# Frontend
cd frontend
npm run test
npm run test:coverage
```

---

## 🤝 Contribuição

Contribuições são bem-vindas!

1. Fork o repositório
2. Crie uma feature branch (`git checkout -b feature/gap-X`)
3. Commit mudanças (`git commit -m 'feat: Description'`)
4. Push (`git push origin feature/gap-X`)
5. Abra um PR

### Padrões

**Commits:**
```bash
feat: Add new feature (Gap #X)
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Refactor code
```

**Python:** Type hints obrigatórios
```python
async def create_item(data: ItemCreate, db: AsyncSession) -> Item:
    """Docstring."""
    ...
```

**TypeScript:** Interfaces tipadas
```typescript
interface User {
  id: string;
  email: string;
}
```

---

## 🔒 Segurança

- ✅ RLS (Row-Level Security) no PostgreSQL
- ✅ JWT com refresh token (15min access, 7days refresh)
- ✅ Bcrypt + salt para senhas
- ✅ HTTPS em produção
- ✅ Input validation com Pydantic
- ✅ CORS configurável

Veja [MULTITENANT_RLS.md](./backend/MULTITENANT_RLS.md).

---

## 📁 Estrutura do Projeto

```
financial_application/
├── backend/                      # FastAPI + Python
│   ├── app/
│   │   ├── api/v1/              # Routes
│   │   ├── core/                # Config, security, deps
│   │   │   ├── tenant_context.py
│   │   │   ├── tenant_middleware.py
│   │   │   └── tenant_decorators.py
│   │   ├── models/              # SQLAlchemy ORM
│   │   ├── schemas/             # Pydantic
│   │   ├── services/            # Business logic
│   │   └── workers/             # Celery tasks
│   ├── migrations/              # Alembic
│   ├── tests/
│   ├── MULTITENANT_RLS.md
│   └── pyproject.toml
├── frontend/                     # Next.js + React
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   └── (dashboard)/     # 11 páginas
│   │   ├── components/
│   │   ├── hooks/               # React Query
│   │   └── stores/              # Zustand
│   ├── HOOKS_DOCUMENTATION.md
│   └── package.json
├── docker-compose.yml
├── README.md                     # Este arquivo
└── pendencias.md                 # Status de implementação
```

---

## 📝 Licença

MIT © 2026 wfcs

---

## 💬 Suporte

- 📧 Issues: [GitHub Issues](https://github.com/wfcs/financial_application/issues)
- 📖 Documentação: [Wiki](https://github.com/wfcs/financial_application/wiki)

---

**Feito com ❤️ para controle financeiro pessoal**

*"Visualize suas finanças, entenda seus padrões, conquiste seus objetivos."*
