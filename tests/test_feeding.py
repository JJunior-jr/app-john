"""Testes para o endpoint de amamentação."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_bottle_feeding(client: AsyncClient):
    """Deve registrar mamadeira com ML ofertados e consumidos."""
    response = await client.post(
        "/api/feeding",
        json={"feeding_type": "bottle", "ml_offered": 100, "ml_consumed": 80},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["feeding_type"] == "bottle"
    assert data["ml_offered"] == 100
    assert data["ml_consumed"] == 80
    assert data["breast_side"] is None
    assert "recorded_at" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_create_breast_feeding_left(client: AsyncClient):
    """Deve registrar amamentação no peito esquerdo."""
    response = await client.post(
        "/api/feeding",
        json={"feeding_type": "breast", "breast_side": "left"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["feeding_type"] == "breast"
    assert data["breast_side"] == "left"
    assert data["ml_offered"] is None


@pytest.mark.asyncio
async def test_create_breast_feeding_right(client: AsyncClient):
    """Deve registrar amamentação no peito direito."""
    response = await client.post(
        "/api/feeding",
        json={"feeding_type": "breast", "breast_side": "right"},
    )
    assert response.status_code == 201
    assert response.json()["breast_side"] == "right"


@pytest.mark.asyncio
async def test_create_breast_feeding_both(client: AsyncClient):
    """Deve registrar amamentação nos dois peitos."""
    response = await client.post(
        "/api/feeding",
        json={"feeding_type": "breast", "breast_side": "both"},
    )
    assert response.status_code == 201
    assert response.json()["breast_side"] == "both"


@pytest.mark.asyncio
async def test_bottle_without_ml_offered_fails(client: AsyncClient):
    """Mamadeira sem ML ofertados deve retornar erro de validação."""
    response = await client.post(
        "/api/feeding",
        json={"feeding_type": "bottle"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_breast_without_side_fails(client: AsyncClient):
    """Peito sem lado especificado deve retornar erro de validação."""
    response = await client.post(
        "/api/feeding",
        json={"feeding_type": "breast"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_feedings_by_date(client: AsyncClient):
    """Deve listar registros filtrados por data."""
    # Cria dois registros (data automática = hoje)
    await client.post(
        "/api/feeding",
        json={"feeding_type": "bottle", "ml_offered": 100, "ml_consumed": 90},
    )
    await client.post(
        "/api/feeding",
        json={"feeding_type": "breast", "breast_side": "left"},
    )

    from datetime import date
    today = date.today().isoformat()
    response = await client.get(f"/api/feeding?date={today}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_feedings_empty_date(client: AsyncClient):
    """Data sem registros deve retornar lista vazia."""
    response = await client.get("/api/feeding?date=2000-01-01")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_delete_feeding(client: AsyncClient):
    """Deve deletar um registro existente."""
    create_resp = await client.post(
        "/api/feeding",
        json={"feeding_type": "bottle", "ml_offered": 50, "ml_consumed": 50},
    )
    record_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/feeding/{record_id}")
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_feeding_not_found(client: AsyncClient):
    """Deletar registro inexistente deve retornar 404."""
    response = await client.delete("/api/feeding/9999")
    assert response.status_code == 404
