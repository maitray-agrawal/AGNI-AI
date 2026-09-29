"""
Phase 1 Tests: FastAPI Foundation & Core Endpoints
==================================================
Tests GET /health, GET /events, and GET /signals endpoints.
Validates that output strictly matches canonical Pydantic schemas.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.canonical import Event, RiskSignal


@pytest.fixture
def client():
    return TestClient(app)


def test_get_health_endpoints(client):
    """Verifies health check endpoint at both /health and /api/health."""
    for url in ("/health", "/api/health"):
        res = client.get(url)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ("healthy", "degraded", "operational")
        assert "version" in data


def test_get_events_endpoints(client):
    """Verifies events endpoint returns data conforming to canonical Event schema."""
    for url in ("/events", "/api/events"):
        res = client.get(url)
        assert res.status_code == 200
        events_data = res.json()
        assert isinstance(events_data, list)
        assert len(events_data) > 0
        for item in events_data:
            evt = Event(**item)
            assert evt.event_id is not None
            assert evt.severity in ("critical", "high", "elevated", "moderate", "low", "info")


def test_get_signals_endpoints(client):
    """Verifies signals endpoint returns data conforming to canonical RiskSignal schema."""
    for url in ("/signals", "/api/signals"):
        res = client.get(url)
        assert res.status_code == 200
        signals_data = res.json()
        assert isinstance(signals_data, list)
        assert len(signals_data) > 0
        for item in signals_data:
            sig = RiskSignal(**item)
            assert sig.signal_id is not None
            assert 0.0 <= sig.risk_score <= 100.0
            assert sig.components is not None
