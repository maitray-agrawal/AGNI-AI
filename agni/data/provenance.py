"""
AGNI Epistemic Data Provenance Structure
========================================
Explicitly tracks and verifies the epistemic state of every intelligence data point:
- OBSERVED: Direct empirical telemetry (e.g. verified AIS signal, exchange tick, customs filing)
- DERIVED: Rule-based calculations (e.g. geometric distance, moving averages, corridor deviation)
- MODELLED: Statistical/econometric model outputs (e.g. GARCH volatility, regime classification)
- SCENARIO: Hypothetical shock projections (e.g. adverse stress-test parameters)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from backend.app.schemas.canonical import Evidence, EvidenceState


class ProvenanceRecord(BaseModel):
    """Immutable audit record establishing the provenance and epistemic status of an entity."""
    record_id: str
    target_entity_id: str
    epistemic_state: EvidenceState
    source_name: str
    source_uri: Optional[str] = None
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    hash_sha256: Optional[str] = None
    verification_notes: Optional[str] = None

    @classmethod
    def create(
        cls,
        entity_id: str,
        state: EvidenceState,
        source: str,
        confidence: float = 1.0,
        notes: str = None,
    ) -> "ProvenanceRecord":
        import hashlib
        rec_id = f"prov-{entity_id}-{state.lower()}"
        h = hashlib.sha256(f"{entity_id}:{state}:{source}:{confidence}".encode()).hexdigest()
        return cls(
            record_id=rec_id,
            target_entity_id=entity_id,
            epistemic_state=state,
            source_name=source,
            confidence=confidence,
            hash_sha256=h,
            verification_notes=notes,
        )


class EpistemicProvenanceAuditor:
    """Audits collections of research entities to guarantee zero epistemic confusion."""

    @staticmethod
    def audit_evidence(evidence_list: List[Evidence]) -> Dict[str, Any]:
        breakdown = {"OBSERVED": 0, "DERIVED": 0, "MODELLED": 0, "SCENARIO": 0}
        total = len(evidence_list)
        for ev in evidence_list:
            if ev.evidence_state in breakdown:
                breakdown[ev.evidence_state] += 1

        pcts = {k: round(v / total * 100, 1) if total > 0 else 0.0 for k, v in breakdown.items()}
        return {
            "total_evidence_count": total,
            "counts": breakdown,
            "percentages": pcts,
            "is_valid": total > 0 and all(k in breakdown for k in pcts),
        }
