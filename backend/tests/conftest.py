"""
Fixtures compartilhadas entre todos os testes.
Usa SQLite em memória para não precisar de PostgreSQL no CI.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import Base, get_session

# ── Banco de dados in-memory para testes ─────────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, autoflush=False
)


async def override_get_session():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_session] = override_get_session


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
async def setup_db():
    """Recria o schema antes de cada teste."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> dict:
    """Retorna client + token de usuário já registrado."""
    res = await client.post("/api/v1/auth/register", json={
        "email": "dev@visor.app",
        "password": "Senha@123",
        "full_name": "Dev Visor",
    })
    token = res.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return {"client": client, "token": token}


@pytest_asyncio.fixture
async def sample_account(auth_client: dict) -> dict:
    """Cria uma conta e retorna o JSON da resposta."""
    client: AsyncClient = auth_client["client"]
    res = await client.post("/api/v1/accounts/", json={
        "name": "Nubank",
        "institution_name": "Nubank",
        "type": "checking",
        "balance": "1500.00",
    })
    assert res.status_code == 201
    return res.json()
