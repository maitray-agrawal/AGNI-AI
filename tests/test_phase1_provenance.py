"""
Phase 1 Tests: Data Provenance & Epistemic Audit
================================================
Validates explicit separation of OBSERVED, DERIVED, MODELLED, and SCENARIO data.
"""

import pytest
from agni.data.provenance import ProvenanceRecord, EpistemicProvenanceAuditor
from agni.research.provenance import ResearchProvenanceManager
from backend.app.schemas.canonical import Evidence


def test_provenance_record_creation():
    rec = ProvenanceRecord.create(
        entity_id="obs-brent-001",
        state="OBSERVED",
        source="ICE Benchmark Exchange",
        confidence=0.99,
        notes="Primary settlement tick",
    )
    assert rec.epistemic_state == "OBSERVED"
    assert rec.hash_sha256 is not None
    assert len(rec.hash_sha256) == 64


def test_epistemic_provenance_auditor():
    evidences = [
        Evidence(evidence_id="e1", evidence_state="OBSERVED", source_name="AIS", headline="Coordinate Verified", confidence=0.99),
        Evidence(evidence_id="e2", evidence_state="DERIVED", source_name="Kinematics", headline="Speed Shift", confidence=0.92),
        Evidence(evidence_id="e3", evidence_state="MODELLED", source_name="GARCH", headline="Vol Projected", confidence=0.85),
        Evidence(evidence_id="e4", evidence_state="SCENARIO", source_name="Stress Engine", headline="Severe Shock", confidence=0.75),
    ]
    report = EpistemicProvenanceAuditor.audit_evidence(evidences)
    assert report["is_valid"] is True
    assert report["counts"]["OBSERVED"] == 1
    assert report["counts"]["DERIVED"] == 1
    assert report["counts"]["MODELLED"] == 1
    assert report["counts"]["SCENARIO"] == 1
    assert report["percentages"]["OBSERVED"] == 25.0


def test_research_provenance_manager():
    evidences = [
        Evidence(evidence_id="e1", evidence_state="OBSERVED", source_name="AIS", headline="Coordinate Verified", confidence=0.99),
        Evidence(evidence_id="e2", evidence_state="MODELLED", source_name="GARCH", headline="Vol Projected", confidence=0.85),
    ]
    res = ResearchProvenanceManager.classify_provenance(evidences)
    assert res["total_records"] == 2
    assert res["breakdown"]["OBSERVED"] == 1
    assert res["breakdown"]["MODELLED"] == 1
    assert ResearchProvenanceManager.validate_epistemic_state("OBSERVED") is True
    assert ResearchProvenanceManager.validate_epistemic_state("UNKNOWN_STATE") is False
