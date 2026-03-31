# 📋 Análise de Pendências e Dívida Técnica — FinControl

> **Data da Análise:** 19 de Março de 2026  
> **Versão do Projeto:** 0.1.0  
> **Status Geral:** 100% Funcional (53/53 tasks core), mas com limitações de produção

---

## 📊 Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de Issues Identificados** | 25 |
| **Críticos (🔴)** | 5 |
| **Altos (🟠)** | 8 |
| **Médios (🟡)** | 8 |
| **Baixos (🔵)** | 4 |
| **Esforço Total Estimado** | 180-220 horas |
| **Prioridade Imediata** | Segurança + Produção |

---

## 🔴 CRÍTICO — Resolva Antes de Ir Para Produção

### 1. **SECRET_KEY Hardcoded e Gerenciamento de Secrets**
- **Severidade:** 🔴 CRÍTICO
- **Impacto:** Comprometimento total da segurança
- **Descrição:**
  - `.env.example` contém chaves padrão (SECRET_KEY, DB passwords)
  - Variáveis sensíveis expostas em plaintext
  - Secrets armazenados em repositório Git (risco enorme)
- **Localhost Atual:**
  ```python
  # backend/app/core/config.py
  SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-me")  # ❌ INSEGURO
  ```
- **Solução Recomendada:**
  1. Usar **AWS Secrets Manager** (Terraform já criado)
  2. Ou **HashiCorp Vault**
  3. Ou **Python-Dotenv** com `.env` gitignored
  4. Rotacionar todas as chaves atuais
- **Arquivos Afetados:**
  - `backend/app/core/config.py`
  - `.env.example` (remover secrets)
  - `docker-compose.yml` (não expor credenciais)
- **Estimativa:** 8-12 horas
- **Checklist:**
  ```
  [ ] Implementar AWS Secrets Manager client
  [ ] Criar lambda/service para carregar secrets
  [ ] Remover secrets de .env.example
  [ ] Rotacionar chaves existentes
  [ ] Adicionar secret rotação automática
  [ ] Testar em dev/staging/prod
  ```

---

### 2. **JWT em localStorage — Vulnerabilidade XSS + CSRF**
- **Severidade:** 🔴 CRÍTICO
- **Impacto:** Session hijacking, XSS attacks
- **Descrição:**
  - Frontend armazena JWT em `localStorage` (acessível via JavaScript)
  - Qualquer XSS consegue roubar o token
  - Sem proteção CSRF em formulários
- **Código Atual:**
  ```typescript
  // frontend/src/stores/auth-store.ts
  setToken: (token) => {
    localStorage.setItem("jwt_token", token);  // ❌ XSS VULNERABLE
  }
  ```
- **Solução:** Migrar para **httpOnly Cookies + CSRF Token**
  ```typescript
  // ✅ SEGURO
  // 1. Backend seta cookie httpOnly
  response.set_cookie(
    "session_id",
    access_token,
    httponly=True,
    secure=True,
    samesite="Lax"
  )
  
  // 2. Frontend envia CSRF token em X-CSRF-Token header
  // 3. Backend valida contra session
  ```
- **Arquivos Afetados:**
  - `backend/app/core/security.py` (adicionar CSRF)
  - `frontend/src/stores/auth-store.ts` (remover localStorage)
  - `frontend/src/lib/api.ts` (usar credentials: "include")
  - `backend/app/main.py` (adicionar CsrfMiddleware)
- **Estimativa:** 16-20 horas
- **Checklist:**
  ```
  [ ] Implementar CSRF token generation no backend
  [ ] Adicionar CsrfMiddleware em FastAPI
  [ ] Mover autenticação para httpOnly cookies
  [ ] Atualizar auth-store para não usar localStorage
  [ ] Adicionar CSRF token no useAuth hook
  [ ] Testar em dev/staging
  [ ] Teste de segurança (manual)
  ```

---

### 3. **CORS Aberto Para Todo o Mundo**
- **Severidade:** 🔴 CRÍTICO
- **Impacto:** CORS attacks, dados expostos
- **Descrição:**
  - CORS configurado com `allow_origins=["*"]`
  - Qualquer domínio consegue fazer requisições
  - Com credentials=True, expõe ainda mais dados
- **Código Atual:**
  ```python
  # backend/app/main.py
  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ ABERTO
    allow_methods=["*"],
    allow_headers=["*"],
  )
  ```
- **Solução:** Whitelist por ambiente
  ```python
  ✅ CORS_ORIGINS = {
    "development": ["http://localhost:3000"],
    "staging": ["https://staging.fincontrol.com"],
    "production": ["https://fincontrol.com"],
  }
  ```
- **Arquivos Afetados:**
  - `backend/app/main.py`
  - `backend/app/core/config.py`
- **Estimativa:** 2-4 horas
- **Checklist:**
  ```
  [ ] Adicionar CORS_ORIGINS em config.py
  [ ] Parametrizar allow_origins/allow_methods
  [ ] Adicionar allow_credentials=False por padrão
  [ ] Testar cross-domain requests bloqueadas
  [ ] Documentar CORS policy
  ```

---

### 4. **Sem Rate Limiting — Brute Force + DDoS Vulnerável**
- **Severidade:** 🔴 CRÍTICO
- **Impacto:** Força bruta em auth, DDoS
- **Descrição:**
  - Endpoints de login/register sem proteção
  - Qualquer IP consegue fazer 1000+ requisições/segundo
  - Sem throttling em webhooks
- **Endpoints Vulneráveis:**
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `POST /webhooks/*`
  - `POST /billing/webhook`
- **Solução:** Implementar rate limiting com **SlowAPI**
  ```python
  ✅ from slowapi import Limiter
  
  limiter = Limiter(key_func=get_remote_address)
  
  @router.post("/login")
  @limiter.limit("5/minute")  # 5 tentativas/minuto
  async def login(...):
      ...
  
  # Diferentes rates por tipo
  - Auth endpoints: 5 req/min por IP
  - API endpoints: 100 req/min por user
  - Webhooks: 1000 req/min por IP
  ```
- **Alternativas:**
  1. **SlowAPI** (FastAPI wrapper)
  2. **Nginx rate limiting** (mais eficiente)
  3. **AWS WAF** (em produção)
- **Arquivos Afetados:**
  - `backend/app/main.py`
  - `backend/app/api/v1/auth/routes.py`
  - `backend/app/api/v1/webhooks/routes.py`
  - `backend/pyproject.toml` (adicionar slowapi)
- **Estimativa:** 12-16 horas
- **Checklist:**
  ```
  [ ] Instalar slowapi
  [ ] Criar limiter com Redis backend
  [ ] Adicionar @limiter.limit em auth endpoints
  [ ] Adicionar @limiter.limit em webhooks
  [ ] Adicionar @limiter.limit em API endpoints
  [ ] Configurar rate limits por env
  [ ] Testar com Apache Bench (ab)
  [ ] Documentar rate limits
  ```

---

### 5. **Sem Autenticação Multi-Fator (2FA/MFA)**
- **Severidade:** 🔴 CRÍTICO
- **Impacto:** Contas comprometidas mesmo com senha forte
- **Descrição:**
  - Apenas autenticação por password
  - Sem TOTP/authenticators
  - Sem backup codes
- **Solução:** Implementar **TOTP (Time-based One-Time Password)**
  ```python
  ✅ from pyotp import TOTP
  
  # 1. User ativa 2FA
  secret = pyotp.random_base32()
  qr_code = pyotp.totp.TOTP(secret).provisioning_uri(...)
  
  # 2. User confirma
  if pyotp.TOTP(secret).verify(user_code):
      user.totp_secret = secret
  
  # 3. Login com 2FA
  if user.totp_secret:
      # Pedir código TOTP antes de emitir JWT
  ```
- **Arquivos Afetados:**
  - `backend/app/models/user.py` (adicionar totp_secret, is_2fa_enabled)
  - `backend/app/schemas/auth.py` (LoginWithTOTP)
  - `backend/app/api/v1/auth/routes.py` (novo endpoint /verify-totp)
  - `backend/app/services/auth_service.py` (validação TOTP)
  - `backend/pyproject.toml` (adicionar pyotp)
  - `frontend/src/app/(auth)/` (novo formulário TOTP)
- **Estimativa:** 20-24 horas
- **Checklist:**
  ```
  [ ] Adicionar modelo para TOTP secret no User
  [ ] Criar endpoint /enable-2fa (gera QR code)
  [ ] Criar endpoint /verify-2fa (confirma código)
  [ ] Modificar login flow para pedir TOTP
  [ ] Gerar backup codes
  [ ] Implementar recovery codes storage
  [ ] UI para ativar/desativar 2FA
  [ ] Testes de 2FA flow
  [ ] Documentar 2FA
  ```

---

## 🟠 ALTO — Resolva Antes da v1.0

### 6. **Pluggy Open Finance Sync — Apenas Stubs**
- **Severidade:** 🟠 ALTO
- **Impacto:** Feature principal não funciona
- **Descrição:**
  - `BE-04` (Open Finance Integration) está como PENDENTE
  - Endpoints stubs retornam dados fake
  - Sincronização não funciona
  - Webhooks não processam dados reais
- **Status Atual:**
  - ✅ Autenticação com Pluggy
  - ✅ Connect token gerado
  - ❌ Sincronização de contas
  - ❌ Sincronização de transações
  - ❌ Processamento de webhooks
- **O que falta:**
  ```python
  # 1. pluggy_sync_service.py precisa:
  - fetch_accounts_from_pluggy() → real API call
  - fetch_transactions_from_pluggy() → real API call
  - sync_to_database() → salvar no BD
  
  # 2. webhook processing:
  - item/updated → fetch novo sync
  - transaction/created → criar transaction
  - account/updated → atualizar saldo
  
  # 3. Error handling:
  - Rate limits da Pluggy
  - Retry logic
  - Dead letter queue
  ```
- **Arquivos Afetados:**
  - `backend/app/services/pluggy_sync_service.py` (implementar)
  - `backend/app/api/v1/webhooks/routes.py` (processar eventos)
  - `backend/app/workers/tasks.py` (async tasks)
  - `backend/tests/test_pluggy_integration.py` (testes)
- **Estimativa:** 40-50 horas
- **Documentação:** [Pluggy API Docs](https://docs.pluggy.ai/)
- **Checklist:**
  ```
  [ ] Estudar API Pluggy completamente
  [ ] Implementar fetch_accounts_from_pluggy
  [ ] Implementar fetch_transactions_from_pluggy
  [ ] Adicionar mapping Pluggy types → BD
  [ ] Implementar webhook processor completo
  [ ] Adicionar retry logic com backoff
  [ ] Implementar dead letter queue
  [ ] Testes de sincronização
  [ ] Testes de webhook
  [ ] Documentação Pluggy flow
  ```

---

### 7. **N+1 Query Problem — Performance Crítica**
- **Severidade:** 🟠 ALTO
- **Impacto:** Queries lentíssimas com muitos dados
- **Descrição:**
  - Relationships carregam sem eager loading
  - Cada transação faz query extra para categoria
  - Dashboard faz 20+ queries para 1 request
- **Exemplo Problemático:**
  ```python
  # ❌ N+1 QUERY
  transactions = await session.execute(
    select(Transaction).where(Transaction.tenant_id == tenant_id)
  )
  
  for tx in transactions:  # N queries aqui!
      category = await category_service.get(tx.category_id)
  
  # ✅ SOLUÇÃO: Eager loading
  transactions = await session.execute(
    select(Transaction)
    .options(selectinload(Transaction.category))
    .where(Transaction.tenant_id == tenant_id)
  )
  ```
- **Endpoints Afetados:**
  - `GET /transactions` (multiplos joins)
  - `GET /dashboard` (multiplas agregações)
  - `GET /cashflow` (por mês)
  - `GET /accounts` (com saldos)
- **Solução:**
  1. Adicionar `selectinload()` em queries grandes
  2. Implementar query result caching (Redis)
  3. Adicionar índices compostos
  4. Usar `joinedload()` para relationships simples
- **Arquivos Afetados:**
  - `backend/app/services/transaction_service.py`
  - `backend/app/services/account_service.py`
  - `backend/app/services/cashflow_service.py`
  - `backend/app/api/v1/dashboard/routes.py`
- **Estimativa:** 20-28 horas
- **Checklist:**
  ```
  [ ] Profilear queries com SQLAlchemy logging
  [ ] Identificar N+1 queries
  [ ] Adicionar selectinload/joinedload
  [ ] Adicionar query caching em Redis
  [ ] Criar índices compostos
  [ ] Benchmark antes/depois
  [ ] Documentar padrão eager loading
  [ ] Adicionar testes de performance
  ```

---

### 8. **Frontend Sem Testes Automatizados**
- **Severidade:** 🟠 ALTO
- **Impacto:** Regressões não detectadas
- **Descrição:**
  - 0 testes React
  - 0 testes E2E
  - 0 testes de integração
  - CI pipeline não testa frontend
- **O que testar:**
  - Components (Buttons, Forms, Tables)
  - Hooks (useAuth, useAccounts, etc)
  - Pages (auth flow, CRUD)
  - Integration (API calls)
  - E2E (workflows completos)
- **Tech Stack Sugerido:**
  - **Unit/Integration:** Vitest + React Testing Library
  - **E2E:** Playwright ou Cypress
- **Arquivos a Criar:**
  - `frontend/__tests__/` (structure)
  - `frontend/vitest.config.ts`
  - `frontend/playwright.config.ts`
  - `frontend/tests/e2e/` (workflows)
- **Estimativa:** 32-40 horas
- **Checklist:**
  ```
  [ ] Setup Vitest
  [ ] Configurar React Testing Library
  [ ] Escrever testes para hooks (useAuth, useAccounts)
  [ ] Testar auth flow
  [ ] Testar CRUD operations
  [ ] Setup Playwright
  [ ] Escrever E2E tests
  [ ] Integrar testes no CI
  [ ] Atingir 60%+ coverage
  ```

---

### 9. **Redis Configurado Mas Não Utilizado**
- **Severidade:** 🟠 ALTO
- **Impacto:** Queries redundantes, performance ruim
- **Descrição:**
  - Redis container rodando (docker-compose)
  - Celery usa (broker + backend)
  - Mas **caching de dados não implementado**
  - Sem cache de auth tokens
  - Sem cache de planos de usuário
- **O que cachear:**
  ```python
  # Candidates para cache
  1. User plans (ttl: 24h)
  2. Auth tokens (ttl: 30m)
  3. Categories list (ttl: 1h)
  4. Dashboard KPIs (ttl: 15m)
  5. Monthly aggregations (ttl: 1h)
  ```
- **Implementação:**
  ```python
  from redis import Redis
  from fastapi_cache2 import FastAPICache2
  from fastapi_cache2.backends.redis import RedisBackend
  
  @app.on_event("startup")
  async def init_cache():
      redis = RedisBackend(Redis.from_url("redis://localhost"))
      FastAPICache2.init(redis)
  
  @router.get("/accounts")
  @cached(namespace="accounts", expire=3600)
  async def get_accounts(...):
      ...
  ```
- **Arquivos Afetados:**
  - `backend/app/main.py` (init cache)
  - `backend/app/services/*` (adicionar @cached)
  - `backend/pyproject.toml` (fastapi-cache2, redis)
- **Estimativa:** 16-20 horas
- **Checklist:**
  ```
  [ ] Instalar fastapi-cache2 + redis
  [ ] Configurar Redis connection
  [ ] Adicionar cache em GET endpoints
  [ ] Invalidar cache em mutations
  [ ] Implementar cache warming
  [ ] Monitorar cache hits/misses
  [ ] Testes de cache
  [ ] Documentar estratégia cache
  ```

---

### 10. **Swagger/OpenAPI Incompleto**
- **Severidade:** 🟠 ALTO
- **Impacto:** Documentação ruim para devs
- **Descrição:**
  - `/docs` não está completo
  - Schemas não documentados
  - Responses não descrevem campos
  - Exemplos faltando
- **O que falta:**
  ```python
  # ❌ Atual
  @router.post("/transactions")
  async def create_transaction(data: TransactionCreate):
      pass
  
  # ✅ Desejado
  @router.post(
      "/transactions",
      responses={
          201: {
              "content": {
                  "application/json": {
                      "example": {
                          "id": "...",
                          "amount": 100.00,
                          ...
                      }
                  }
              }
          },
          400: {"description": "Invalid data"},
          401: {"description": "Unauthorized"},
      },
      tags=["transactions"],
      summary="Create transaction",
      description="Creates a new transaction for the authenticated user"
  )
  async def create_transaction(...):
      pass
  ```
- **Arquivos Afetados:**
  - `backend/app/main.py` (title, description, openapi_tags)
  - `backend/app/api/v1/**/routes.py` (adicionar docs)
  - `backend/app/schemas/*` (adicionar examples)
- **Estimativa:** 12-16 horas
- **Checklist:**
  ```
  [ ] Adicionar título/description na app
  [ ] Documentar cada endpoint
  [ ] Adicionar exemplos em schemas
  [ ] Documentar error responses
  [ ] Adicionar tags por módulo
  [ ] Testar /docs visualmente
  [ ] Gerar OpenAPI JSON
  [ ] Publicar em Swagger UI online
  ```

---

### 11. **Logging Inadequado — Sem Correlation IDs**
- **Severidade:** 🟠 ALTO
- **Impacto:** Debugging em produção impossível
- **Descrição:**
  - Logs apenas em console
  - Sem estrutura (JSON)
  - Sem correlation IDs entre requests
  - Sem rastreamento de contexto tenant
- **Problema:**
  ```
  # Atual
  2026-03-19 10:30:45 ERROR Error creating account
  2026-03-19 10:30:46 ERROR Failed to sync transactions
  
  # Como saber qual request/user/tenant gerou o erro?
  ```
- **Solução:**
  ```python
  ✅ from pythonjsonlogger import jsonlogger
  from contextvars import ContextVar
  
  request_id: ContextVar[str] = ContextVar("request_id")
  tenant_id: ContextVar[str] = ContextVar("tenant_id")
  user_id: ContextVar[str] = ContextVar("user_id")
  
  # Middleware
  @app.middleware("http")
  async def log_requests(request, call_next):
      request_id.set(str(uuid4()))
      # ... tenant_id, user_id
      
  # Log estruturado
  logger.info("create_account", extra={
      "request_id": request_id.get(),
      "tenant_id": tenant_id.get(),
      "user_id": user_id.get(),
      "account_id": account.id,
  })
  ```
- **Arquivos Afetados:**
  - `backend/app/core/logging.py` (novo arquivo)
  - `backend/app/main.py` (adicionar middleware)
  - `backend/app/**/*.py` (usar logger estruturado)
- **Estimativa:** 16-20 horas
- **Checklist:**
  ```
  [ ] Setup JSON logging
  [ ] Criar context vars (request_id, tenant_id, user_id)
  [ ] Adicionar logging middleware
  [ ] Refatorar logs para estruturado
  [ ] Integrar com CloudWatch
  [ ] Configurar centralized logging
  [ ] Testes de logging
  [ ] Documentar padrão
  ```

---

### 12. **Celery Sem Retry/Dead Letter Queue**
- **Severidade:** 🟠 ALTO
- **Impacto:** Tasks falham silenciosamente
- **Descrição:**
  - Tasks configuradas mas sem retry logic
  - Falhas não são rastreadas
  - Sem dead letter queue (DLQ)
  - Sem monitoring
- **Exemplo Atual:**
  ```python
  # ❌ Sem retry
  @celery_app.task
  def process_webhook(event_id):
      # Se falhar... ninguém sabe
      pass
  ```
- **Solução:**
  ```python
  ✅ @celery_app.task(
      autoretry_for=(Exception,),
      retry_kwargs={'max_retries': 3},
      retry_backoff=True,
      retry_backoff_max=600,
      retry_jitter=True,
      acks_late=True,
  )
  def process_webhook(event_id):
      try:
          # ...
      except Exception as e:
          logger.error(f"Webhook processing failed", extra={"event_id": event_id})
          # Avisar DLQ
          raise
  ```
- **Implementação:**
  - Adicionar `MAX_RETRIES`, `RETRY_BACKOFF` em config
  - Implementar Dead Letter Queue (exchange especial)
  - Monitorar DLQ com alertas
  - Dashboard para ver tarefas falhadas
- **Arquivos Afetados:**
  - `backend/app/workers/tasks.py` (adicionar retry config)
  - `backend/app/core/config.py` (CELERY settings)
  - `backend/app/workers/celery_app.py` (setup)
- **Estimativa:** 12-16 horas
- **Checklist:**
  ```
  [ ] Adicionar retry config em tasks
  [ ] Implementar Dead Letter Queue
  [ ] Criar task failure handler
  [ ] Setup monitoring de tasks
  [ ] Criar dashboard para DLQ
  [ ] Alertas para task failures
  [ ] Testes de retry behavior
  [ ] Documentar task architecture
  ```

---

### 13. **CI/CD Parcial — GitHub Actions Templates Criados Mas Não em Uso**
- **Severidade:** 🟠 ALTO
- **Impacto:** Deploy manual, sem automação
- **Descrição:**
  - `.github/workflows/` criado mas workflows não ativados
  - CI pipeline template pronto mas desabilitado
  - Deploy template pronto mas manual
  - Sem auto-deploy em push para main
- **O que está criado:**
  - `ci.yml` (backend tests + lint + frontend build)
  - `deploy.yml` (manual dispatch, ECR push, ECS deploy)
- **O que falta:**
  - Ativar CI pipeline
  - Trigger automático em push/PR
  - Setup secretos no GitHub (AWS credentials)
  - Ambiente staging funcional
  - Auto-deploy em prod
- **Arquivos Afetados:**
  - `.github/workflows/ci.yml` (ajustar triggers)
  - `.github/workflows/deploy.yml` (habilitar auto-deploy)
  - GitHub repository settings (secrets)
  - AWS IAM (criar user para CI/CD)
- **Estimativa:** 16-20 horas
- **Checklist:**
  ```
  [ ] Criar GitHub Actions secrets (AWS access keys)
  [ ] Ativar CI pipeline em push/PR
  [ ] Configurar build matrix (Python versions)
  [ ] Setup deploy para staging
  [ ] Setup deploy para production
  [ ] Testar pipeline end-to-end
  [ ] Documentar CI/CD process
  [ ] Configurar branch protection rules
  [ ] Setup notifications (Slack/Email)
  ```

---

## 🟡 MÉDIO — Próxima Fase

### 14. **Terraform Criado Mas Não Deployado**
- **Severidade:** 🟡 MÉDIO
- **Impacto:** Infraestrutura drift, deploy manual
- **O que está pronto:**
  - VPC com 2 AZs
  - RDS PostgreSQL 16
  - ElastiCache Redis
  - ECS cluster
  - ECR repository
- **O que falta:**
  - Terraform apply em AWS
  - Setup de segredos (AWS Secrets Manager)
  - Load balancer (ALB)
  - Auto scaling groups
  - Monitoramento (CloudWatch)
- **Estimativa:** 24-32 horas

---

### 15. **Deploys Sem Downtime Mínimo**
- **Severidade:** 🟡 MÉDIO
- **Problema:**
  - Sem health checks adequados
  - Sem rolling deployments
  - Migrações de BD podem quebrar
- **Solução:**
  - Implementar health checks
  - ECS rolling deployment strategy
  - Alembic migrations com rollback
  - Canary deployments
- **Estimativa:** 12-16 horas

---

### 16. **Sem Testes de Integração End-to-End**
- **Severidade:** 🟡 MÉDIO
- **Descrição:**
  - Testes unitários existem
  - Mas faltam testes de fluxo completo
  - Auth → Create Account → Create Transaction → Export
- **Estimativa:** 16-20 horas

---

### 17. **Documentação de API Incompleta**
- **Severidade:** 🟡 MÉDIO
- **Falta:**
  - Guia de endpoints
  - Exemplos de requests/responses
  - Guia de rate limits
  - Error codes documentados
- **Estimativa:** 8-12 horas

---

### 18. **Sem Teste de Carga (Load Testing)**
- **Severidade:** 🟡 MÉDIO
- **Descrição:**
  - Como a API se comporta com 1000 usuários?
  - Dashboard aguenta 100 requisições/segundo?
  - Redis hit rate adequado?
- **Ferramenta:** Locust ou K6
- **Estimativa:** 12-16 horas

---

### 19. **Verificação de Licenças de Dependências**
- **Severidade:** 🟡 MÉDIO
- **Problema:**
  - Sem audit de dependências open-source
  - Poderiam ter licenças incompatíveis (GPL)
  - Sem SBOM (Software Bill of Materials)
- **Ferramentas:** OWASP Dependency-Check, Snyk
- **Estimativa:** 4-6 horas

---

### 20. **Sem API Versionamento Explícito**
- **Severidade:** 🟡 MÉDIO
- **Descrição:**
  - API `/v1/` existe mas sem estratégia de versioning
  - Como lidar com quebras de compatibilidade?
  - Sem deprecation warnings
- **Estimativa:** 6-8 horas

---

### 21. **Performance Otimização Frontend**
- **Severidade:** 🟡 MÉDIO
- **Falta:**
  - Code splitting por rota
  - Lazy loading de componentes
  - Image optimization
  - Performance monitoring
- **Estimativa:** 16-20 horas

---

## 🔵 BAIXO — Nice to Have

### 22. **Monitoramento e Observabilidade Incompleto**
- **Sentry** implementado mas não fully configured
- **CloudWatch** logs sem dashboards
- Faltam métricas de negócio (conversão, churn, MRR)
- **Estimativa:** 20-24 horas

---

### 23. **Documentação de Infraestrutura**
- **Diagrama de arquitetura** faltando
- **Runbooks** para operações comuns
- **Troubleshooting guide**
- **Disaster recovery plan**
- **Estimativa:** 12-16 horas

---

### 24. **Melhorias na Detecção de Padrões Recorrentes**
- **AI Assistant** é apenas rule-based
- Sem Machine Learning para categorização
- Poderia usar clustering para detect recorrências automáticas
- **Estimativa:** 40-60 horas (feature big)

---

### 25. **Feature Flags / Rollout Gradual**
- **Sem feature flags** para A/B testing
- Sem toggles para features experimentais
- Difícil fazer canary deployments
- **Tech:** LaunchDarkly ou Unleash
- **Estimativa:** 16-20 horas

---

## 📊 Matriz de Priorização

| # | Issue | Crítico | Impacto | Esforço | Prioridade | Timeline |
|---|-------|---------|---------|---------|-----------|----------|
| 1 | Secret Key Management | 🔴 | Altíssimo | 12h | **P0** | Week 1 |
| 2 | JWT x2FA + HttpOnly | 🔴 | Altíssimo | 36h | **P0** | Week 2-3 |
| 3 | CORS Whitelist | 🔴 | Alto | 4h | **P0** | Week 1 |
| 4 | Rate Limiting | 🔴 | Alto | 16h | **P0** | Week 2 |
| 5 | 2FA Implementation | 🔴 | Alto | 24h | **P0** | Week 3-4 |
| 6 | Pluggy Sync | 🟠 | Crítico | 50h | **P1** | Week 5-8 |
| 7 | N+1 Query Fixing | 🟠 | Crítico | 28h | **P1** | Week 2-3 |
| 8 | Frontend Tests | 🟠 | Alto | 40h | **P1** | Week 4-6 |
| 9 | Redis Caching | 🟠 | Médio | 20h | **P1** | Week 3 |
| 10 | OpenAPI Docs | 🟠 | Médio | 16h | **P2** | Week 3-4 |
| 11 | Structured Logging | 🟠 | Médio | 20h | **P1** | Week 2 |
| 12 | Celery Reliability | 🟠 | Médio | 16h | **P1** | Week 2-3 |
| 13 | CI/CD Activation | 🟠 | Médio | 20h | **P1** | Week 2-3 |
| 14 | Terraform Deploy | 🟡 | Médio | 32h | **P2** | Week 4-6 |
| 15 | Zero-downtime Deploy | 🟡 | Médio | 16h | **P2** | Week 4 |
| 16 | E2E Testing | 🟡 | Médio | 20h | **P2** | Week 4-5 |
| 17 | API Documentation | 🟡 | Baixo | 12h | **P2** | Week 3 |
| 18 | Load Testing | 🟡 | Médio | 16h | **P2** | Week 5 |
| 19 | Dependency Check | 🟡 | Baixo | 6h | **P3** | Week 1 |
| 20 | API Versioning | 🟡 | Baixo | 8h | **P3** | Week 4 |
| 21 | Frontend Performance | 🟡 | Médio | 20h | **P2** | Week 5 |
| 22 | Monitoring Dashboard | 🔵 | Baixo | 24h | **P3** | Week 6-7 |
| 23 | Infra Documentation | 🔵 | Baixo | 16h | **P3** | Week 7 |
| 24 | ML for Recurrences | 🔵 | Médio | 60h | **P4** | Backlog |
| 25 | Feature Flags | 🔵 | Baixo | 20h | **P3** | Week 8 |

---

## 🚀 Roadmap Recomendado

### **Fase 0: Segurança (Week 1-2) — 16 horas**
```
[ ] Secrets management (AWS Secrets Manager)
[ ] CORS whitelist
[ ] Dependency vulnerability check
Total: 16h
```

### **Fase 1: Produção Ready (Week 2-4) — 100 horas**
```
[ ] JWT httpOnly + CSRF (36h)
[ ] Rate limiting (16h)
[ ] 2FA/MFA (24h)
[ ] Structured logging (20h)
[ ] Celery reliability (16h)
[ ] CI/CD activation (20h)
Total: 132h
```

### **Fase 2: Core Features (Week 5-8) — 110 horas**
```
[ ] Pluggy Open Finance sync (50h)
[ ] N+1 query optimization (28h)
[ ] Redis caching (20h)
[ ] OpenAPI docs (16h)
Total: 114h
```

### **Fase 3: Quality (Week 9-12) — 80 horas**
```
[ ] Frontend tests (40h)
[ ] E2E testing (20h)
[ ] Load testing (16h)
[ ] API documentation (12h)
Total: 88h
```

### **Fase 4: Operations (Week 13-16) — 88 horas**
```
[ ] Terraform deploy (32h)
[ ] Zero-downtime deploy (16h)
[ ] Frontend performance (20h)
[ ] Monitoring dashboard (24h)
Total: 92h
```

**Total Estimado: 428 horas (≈ 10-11 semanas com 1 dev)**

---

## 📝 Notas Gerais

### O que Já Está Excelente ✅
- Arquitetura multi-tenant bem implementada
- Autenticação JWT + refresh tokens
- RLS em PostgreSQL
- Service layer bem estruturado
- Tests unitários sólidos
- Docker + docker-compose
- Stripe integration completa
- Celery + Redis setup
- Terraform IaC base pronto

### O que Precisa Urgentemente ⚠️
- Segurança em geral (secrets, CORS, rate limiting, 2FA)
- Pluggy sync funcional
- Tests frontend
- CI/CD ativado
- Logs estruturados

### Próximos Passos Imediatos
1. **Dia 1:** Secrets management
2. **Dia 2:** CORS + rate limiting
3. **Dia 3-5:** JWT httpOnly + CSRF
4. **Semana 2:** 2FA + structured logging
5. **Semana 3:** Pluggy sync
6. **Semana 4:** Frontend tests + CI/CD

---

## 📞 Como Usar Este Documento

- **Para devs:** Use como backlog no GitHub/Jira
- **Para PO:** Priorize por severidade (🔴 → 🟠 → 🟡 → 🔵)
- **Para lead:** Estime sprints com base na matriz
- **Para ops:** Protocolo para produção: **Fases 0-1 obrigatórias**

---

**Última atualização:** 19 de Março de 2026  
**Próxima revisão:** A cada 2 semanas ou quando 30% das tasks forem completadas
