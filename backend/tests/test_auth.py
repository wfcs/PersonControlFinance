import pytest
from httpx import AsyncClient

# As fixtures `client` e `setup_db` vêm automaticamente do `conftest.py`



@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    res = await client.post("/api/v1/auth/register", json={
        "email": "teste@visor.app",
        "password": "Senha@123",
        "full_name": "Usuário Teste",
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@visor.app",
        "password": "Senha@123",
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "login@visor.app",
        "password": "Senha@123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "errado@visor.app",
        "password": "Senha@123",
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "errado@visor.app",
        "password": "SenhaErrada",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "me@visor.app",
        "password": "Senha@123",
        "full_name": "Walisson",
    })
    token = reg.json()["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@visor.app"
