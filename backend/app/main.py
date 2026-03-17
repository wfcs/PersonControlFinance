from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.tenant_middleware import TenantContextMiddleware
from app.db.session import engine, Base
from app.integrations.pluggy_client import pluggy_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: cria tabelas se não existirem (dev only)
    if not settings.is_production:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await pluggy_client.close()
    await engine.dispose()


app = FastAPI(
    title="Visor API",
    description="API de controle financeiro pessoal com Open Finance",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Tenant Context Middleware ────────────────────────────────────────────────
# Deve vir depois do CORS, injeta tenant_id em toda request
app.add_middleware(TenantContextMiddleware)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV})
