import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    res = await client.post("/api/v1/categories/", json={
        "name": "Alimentação",
        "icon": "🍔",
        "color": "#FF6B6B",
        "monthly_limit": "800.00",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Alimentação"
    assert data["parent_id"] is None


@pytest.mark.asyncio
async def test_create_subcategory(auth_client: dict):
    client: AsyncClient = auth_client["client"]

    parent = await client.post("/api/v1/categories/", json={"name": "Serviços"})
    parent_id = parent.json()["id"]

    child = await client.post("/api/v1/categories/", json={
        "name": "Telecomunicações",
        "parent_id": parent_id,
    })
    assert child.status_code == 201
    assert child.json()["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_list_categories_nested(auth_client: dict):
    client: AsyncClient = auth_client["client"]

    parent = await client.post("/api/v1/categories/", json={"name": "Serviços"})
    parent_id = parent.json()["id"]

    await client.post("/api/v1/categories/", json={"name": "Streaming", "parent_id": parent_id})
    await client.post("/api/v1/categories/", json={"name": "Telecomunicações", "parent_id": parent_id})

    res = await client.get("/api/v1/categories/")
    assert res.status_code == 200
    cats = res.json()

    root = next(c for c in cats if c["id"] == parent_id)
    assert len(root["children"]) == 2


@pytest.mark.asyncio
async def test_update_category(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    cat = await client.post("/api/v1/categories/", json={"name": "Compras"})
    cat_id = cat.json()["id"]

    res = await client.patch(f"/api/v1/categories/{cat_id}", json={
        "monthly_limit": "500.00",
        "color": "#4ECDC4",
    })
    assert res.status_code == 200
    assert float(res.json()["monthly_limit"]) == 500.00


@pytest.mark.asyncio
async def test_delete_category(auth_client: dict):
    client: AsyncClient = auth_client["client"]
    cat = await client.post("/api/v1/categories/", json={"name": "Temporária"})
    cat_id = cat.json()["id"]

    res = await client.delete(f"/api/v1/categories/{cat_id}")
    assert res.status_code == 204

    cats = await client.get("/api/v1/categories/")
    assert all(c["id"] != cat_id for c in cats.json())
