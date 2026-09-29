"""
Tests for AGNI Phase 11: Earth Observation & Satellite Intelligence Module
===========================================================================
Validates:
- Gated research status behavior
- SAR vessel detection extraction
- Chokepoint queue saturation & congestion state escalation
- Anomaly z-score calculations against historical baselines
- REST API endpoints for satellite telemetry
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from agni.satellite.observer import ChokepointSatelliteObserver, satellite_observer, CHOKEPOINT_REGISTRY
from agni.satellite.schemas import ChokepointSARAnalysis, SatelliteModuleStatus


@pytest.fixture
def client():
    return TestClient(app)


def test_satellite_module_gate_status():
    """Confirms module status reflects research gating without external dependencies."""
    status = satellite_observer.get_status()
    assert isinstance(status, SatelliteModuleStatus)
    assert len(status.monitored_chokepoints) >= 5
    assert "strait-of-hormuz" in status.monitored_chokepoints
    assert "bab-el-mandeb" in status.monitored_chokepoints
    assert "SENTINEL-1-SAR (Copernicus)" in status.supported_constellations


def test_chokepoint_sar_baseline_analysis():
    """Tests normal baseline SAR analysis for Strait of Hormuz."""
    observer = ChokepointSatelliteObserver()
    analysis = observer.analyze_chokepoint("strait-of-hormuz", shock_multiplier=1.0)

    assert isinstance(analysis, ChokepointSARAnalysis)
    assert analysis.chokepoint_id == "strait-of-hormuz"
    assert analysis.chokepoint_name == "Strait of Hormuz"
    assert analysis.total_vessels_detected > 0
    assert analysis.anchored_vessels_count >= 0
    assert analysis.transiting_vessels_count > 0
    assert len(analysis.detection_sample) > 0
    assert analysis.provenance_hash.startswith("SHA256:")
    assert -2.0 <= analysis.congestion_anomaly_zscore <= 2.0


def test_chokepoint_sar_congestion_shock_escalation():
    """Tests that a high shock multiplier escalates congestion state and delays."""
    observer = ChokepointSatelliteObserver()
    
    # Baseline
    normal = observer.analyze_chokepoint("bab-el-mandeb", shock_multiplier=1.0)
    # Severe disruption shock (e.g. drone attack / corridor closure)
    shocked = observer.analyze_chokepoint("bab-el-mandeb", shock_multiplier=3.5)

    assert shocked.anchored_vessels_count > normal.anchored_vessels_count
    assert shocked.anchorage_density_index >= normal.anchorage_density_index
    assert shocked.congestion_anomaly_zscore > normal.congestion_anomaly_zscore
    assert shocked.congestion_state in ("CONGESTED", "SEVERELY_BLOCKED")
    assert shocked.estimated_cargo_delay_hours > 0.0


def test_satellite_batch_scan():
    """Validates batch scanning across all registered global chokepoints."""
    observer = ChokepointSatelliteObserver()
    batch = observer.scan_all_chokepoints()

    assert len(batch) == len(CHOKEPOINT_REGISTRY)
    chokepoint_ids = {item.chokepoint_id for item in batch}
    assert "strait-of-hormuz" in chokepoint_ids
    assert "strait-of-malacca" in chokepoint_ids
    assert "suez-canal" in chokepoint_ids
    assert "panama-canal" in chokepoint_ids


def test_api_satellite_endpoints(client):
    """Verifies all FastAPI REST endpoints for satellite telemetry."""
    # 1. Status
    res_status = client.get("/api/satellite/status")
    assert res_status.status_code == 200
    data_status = res_status.json()
    assert "operational_mode" in data_status
    assert "monitored_chokepoints" in data_status

    # 2. Chokepoints list
    res_cps = client.get("/api/satellite/chokepoints")
    assert res_cps.status_code == 200
    cps = res_cps.json()
    assert len(cps) >= 5

    # 3. Analyses list
    res_analyses = client.get("/api/satellite/analyses")
    assert res_analyses.status_code == 200
    analyses = res_analyses.json()
    assert len(analyses) == len(cps)

    # 4. Single chokepoint
    res_single = client.get("/api/satellite/analyses/strait-of-hormuz?shock_multiplier=1.5")
    assert res_single.status_code == 200
    single = res_single.json()
    assert single["chokepoint_id"] == "strait-of-hormuz"

    # 5. Invalid chokepoint 404
    res_404 = client.get("/api/satellite/analyses/non-existent-chokepoint")
    assert res_404.status_code == 404

    # 6. POST scan
    res_scan = client.post("/api/satellite/scan", json={
        "chokepoint_id": "panama-canal",
        "constellation": "SENTINEL-1-SAR",
        "shock_multiplier": 2.0,
    })
    assert res_scan.status_code == 200
    scan_data = res_scan.json()
    assert scan_data["chokepoint_id"] == "panama-canal"
    assert scan_data["anchorage_density_index"] > 0.0
