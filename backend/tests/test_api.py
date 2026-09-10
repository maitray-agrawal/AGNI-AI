import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_api_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert data["environment"] == "sovereign_local"
        assert "ollama_connected" in data
        assert data["qdrant_ready"] is True
        print(f"\n[API Health Status]: {data}")


@pytest.mark.asyncio
async def test_api_models_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "ollama"
        assert len(data["models"]) >= 3
        print(f"\n[API Registered Models]: {[m['id'] for m in data['models']]}")


@pytest.mark.asyncio
async def test_api_security_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/security/status")
        assert response.status_code == 200
        data = response.json()
        assert data["air_gapped"] is True
        assert data["external_ai_api_calls"] == 0
        assert data["external_network_connections"] == 0
        assert data["sandbox_network_isolated"] is True
        print(f"\n[API Security Telemetry]: {data}")


@pytest.mark.asyncio
async def test_api_tasks_run_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "task": "Calculate wall thickness reduction from 8.2 mm to 4.2 mm.",
            "files": [],
            "stream": False,
        }
        response = await ac.post("/api/tasks/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] in ["completed", "completed_with_errors"]
        assert data["selected_model"] is not None
        assert data["task_type"] == "coding_calculation"
        assert data["routing_reason"] is not None
        assert len(data["trace_summary"]) > 0
        print(f"\n[API Task Run E2E]: task_id={data['task_id']}, model={data['selected_model']}, latency={data.get('total_duration_ms')}ms")
