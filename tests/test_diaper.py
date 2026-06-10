"""Testes para o endpoint de troca de fraldas."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_diaper_pee_only(client: AsyncClient):
    """Deve registrar troca com apenas xixi."""
    response = await client.post(
        "/api/diaper",
        json={"has_pee": True, "has_poop": False},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["has_pee"] is True
    assert data["has_poop"] is False
    assert "recorded_at" in data


@pytest.mark.asyncio
async def test_create_diaper_poop_only(client: AsyncClient):
    """Deve registrar troca com apenas coco."""
    response = await client.post(
        "/api/diaper",
        json={"has_pee": False, "has_poop": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["has_pee"] is False
    assert data["has_poop"] is True


@pytest.mark.asyncio
async def test_create_diaper_both(client: AsyncClient):
    """Deve registrar troca com xixi e coco."""
    response = await client.post(
        "/api/diaper",
        json={"has_pee": True, "has_poop": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["has_pee"] is True
    assert data["has_poop"] is True


@pytest.mark.asyncio
async def test_create_diaper_neither_fails(client: AsyncClient):
    """Troca sem xixi nem coco deve retornar erro de validação."""
    response = await client.post(
        "/api/diaper",
        json={"has_pee": False, "has_poop": False},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_diapers_by_date(client: AsyncClient):
    """Deve listar trocas filtradas por data."""
    await client.post("/api/diaper", json={"has_pee": True, "has_poop": False})
    await client.post("/api/diaper", json={"has_pee": False, "has_poop": True})

    from datetime import date
    today = date.today().isoformat()
    response = await client.get(f"/api/diaper?date={today}")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_list_diapers_empty_date(client: AsyncClient):
    """Data sem registros deve retornar lista vazia."""
    response = await client.get("/api/diaper?date=2000-01-01")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_delete_diaper(client: AsyncClient):
    """Deve deletar um registro de troca."""
    create_resp = await client.post(
        "/api/diaper", json={"has_pee": True, "has_poop": False}
    )
    record_id = create_resp.json()["id"]
    delete_resp = await client.delete(f"/api/diaper/{record_id}")
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_diaper_not_found(client: AsyncClient):
    """Deletar troca inexistente deve retornar 404."""
    response = await client.delete("/api/diaper/9999")
    assert response.status_code == 404
