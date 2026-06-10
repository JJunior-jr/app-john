"""Testes para o endpoint de banho."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_bath(client: AsyncClient):
    """Deve registrar um banho com horário automático."""
    response = await client.post("/api/bath")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "recorded_at" in data
    assert "date" in data


@pytest.mark.asyncio
async def test_list_baths_by_date(client: AsyncClient):
    """Deve listar banhos filtrados por data."""
    await client.post("/api/bath")
    await client.post("/api/bath")

    from datetime import date
    today = date.today().isoformat()
    response = await client.get(f"/api/bath?date={today}")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_list_baths_empty_date(client: AsyncClient):
    """Data sem registros deve retornar lista vazia."""
    response = await client.get("/api/bath?date=2000-01-01")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_delete_bath(client: AsyncClient):
    """Deve deletar um registro de banho."""
    create_resp = await client.post("/api/bath")
    record_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/bath/{record_id}")
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_bath_not_found(client: AsyncClient):
    """Deletar banho inexistente deve retornar 404."""
    response = await client.delete("/api/bath/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_bath_recorded_at_is_automatic(client: AsyncClient):
    """O horário do banho deve ser definido automaticamente pelo servidor."""
    from datetime import datetime, timezone
    before = datetime.now(tz=timezone.utc)
    response = await client.post("/api/bath")
    after = datetime.now(tz=timezone.utc)

    assert response.status_code == 201
    raw = response.json()["recorded_at"]
    recorded_at = datetime.fromisoformat(raw)
    # SQLite pode devolver naive datetime — normaliza para UTC
    if recorded_at.tzinfo is None:
        recorded_at = recorded_at.replace(tzinfo=timezone.utc)
    assert before <= recorded_at <= after
