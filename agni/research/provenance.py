"""
AGNI Research Provenance & Epistemic Classification
===================================================
Enforces the 4-tier epistemic state separation:
OBSERVED | DERIVED | MODELLED | SCENARIO
"""

from typing import List, Dict, Any
from backend.app.schemas.canonical import Evidence, EvidenceState


class ResearchProvenanceManager:
    """Manages epistemic evidence classification and verification gates."""

    VALID_STATES: List[EvidenceState] = ["OBSERVED", "DERIVED", "MODELLED", "SCENARIO"]

    @classmethod
    def validate_epistemic_state(cls, state: str) -> bool:
        return state in cls.VALID_STATES

    @classmethod
    def classify_provenance(cls, evidences: List[Evidence]) -> Dict[str, Any]:
        """Classifies a set of evidence records into their strict epistemic categories."""
        categorized: Dict[str, List[Dict[str, Any]]] = {
            "OBSERVED": [],
            "DERIVED": [],
            "MODELLED": [],
            "SCENARIO": [],
        }

        for ev in evidences:
            if ev.evidence_state in categorized:
                categorized[ev.evidence_state].append(ev.model_dump())

        return {
            "total_records": len(evidences),
            "breakdown": {k: len(v) for k, v in categorized.items()},
            "records_by_state": categorized,
        }
