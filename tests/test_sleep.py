"""Testes para o endpoint de sono."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_start_sleep(client: AsyncClient):
    """Deve iniciar um registro de sono com start_time automático."""
    response = await client.post("/api/sleep/start")
    assert response.status_code == 201
    data = response.json()
    assert "start_time" in data
    assert data["end_time"] is None
    assert data["duration_min"] is None
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_end_sleep(client: AsyncClient):
    """Deve finalizar sono ativo e calcular duração."""
    # Inicia sono
    start_resp = await client.post("/api/sleep/start")
    assert start_resp.status_code == 201
    sleep_id = start_resp.json()["id"]

    # Finaliza sono
    end_resp = await client.patch(f"/api/sleep/{sleep_id}/end")
    assert end_resp.status_code == 200
    data = end_resp.json()
    assert data["end_time"] is not None
    assert data["duration_min"] is not None
    assert data["duration_min"] >= 0
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_end_already_ended_sleep_fails(client: AsyncClient):
    """Finalizar sono já encerrado deve retornar erro 400."""
    start_resp = await client.post("/api/sleep/start")
    sleep_id = start_resp.json()["id"]

    await client.patch(f"/api/sleep/{sleep_id}/end")  # Primeira vez OK
    end_again = await client.patch(f"/api/sleep/{sleep_id}/end")  # Segunda vez falha
    assert end_again.status_code == 400


@pytest.mark.asyncio
async def test_end_sleep_not_found(client: AsyncClient):
    """Finalizar sono inexistente deve retornar 404."""
    response = await client.patch("/api/sleep/9999/end")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_active_sleep_when_active(client: AsyncClient):
    """Deve retornar sono ativo quando existir."""
    await client.post("/api/sleep/start")
    response = await client.get("/api/sleep/active")
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert data["end_time"] is None


@pytest.mark.asyncio
async def test_get_active_sleep_when_none(client: AsyncClient):
    """Deve retornar null quando não há sono ativo."""
    response = await client.get("/api/sleep/active")
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_list_sleeps_by_date(client: AsyncClient):
    """Deve listar sonos do dia."""
    # Inicia e finaliza um sono
    start_resp = await client.post("/api/sleep/start")
    sleep_id = start_resp.json()["id"]
    await client.patch(f"/api/sleep/{sleep_id}/end")

    from datetime import date
    today = date.today().isoformat()
    response = await client.get(f"/api/sleep?date={today}")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_sleep_pending_state_in_list(client: AsyncClient):
    """Sono ativo deve aparecer como is_active=True na lista."""
    await client.post("/api/sleep/start")

    from datetime import date
    today = date.today().isoformat()
    response = await client.get(f"/api/sleep?date={today}")
    assert response.status_code == 200
    sleeps = response.json()
    active_sleeps = [s for s in sleeps if s["is_active"]]
    assert len(active_sleeps) >= 1


@pytest.mark.asyncio
async def test_delete_sleep(client: AsyncClient):
    """Deve deletar um registro de sono."""
    start_resp = await client.post("/api/sleep/start")
    sleep_id = start_resp.json()["id"]

    delete_resp = await client.delete(f"/api/sleep/{sleep_id}")
    assert delete_resp.status_code == 204
