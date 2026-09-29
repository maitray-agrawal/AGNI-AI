"""
AGNI Event Validation Engine
============================
Strict semantic and coordinate validation for geopolitical shock events.
Guarantees analytical fidelity before normalization or persistence.
"""

from typing import Dict, Any, List, Tuple
from agni.data.schemas import Event, SeverityLevel, EventType

VALID_SEVERITIES = {"critical", "high", "elevated", "moderate", "low", "info"}
VALID_EVENT_TYPES = {
    "maritime_disruption",
    "energy_disruption",
    "commodity_supply_shock",
    "sanctions",
    "infrastructure_disruption",
    "cyber_kinetic_threat",
    "geopolitical_escalation",
}


class ValidationError(ValueError):
    """Raised when an event fails strict validation checks."""
    pass


class EventValidator:
    """Validates incoming geopolitical event payloads."""

    @classmethod
    def validate_event(cls, event: Event) -> Tuple[bool, List[str]]:
        """
        Validates an instantiated Event model for geographic, semantic,
        and temporal consistency. Returns (is_valid, error_list).
        """
        errors: List[str] = []

        # 1. Geographic boundaries
        if not (-90.0 <= event.latitude <= 90.0):
            errors.append(f"Latitude {event.latitude} out of bounds [-90, 90].")
        if not (-180.0 <= event.longitude <= 180.0):
            errors.append(f"Longitude {event.longitude} out of bounds [-180, 180].")

        # 2. Epistemic confidence bounds
        if not (0.0 <= event.confidence <= 1.0):
            errors.append(f"Confidence {event.confidence} must be within [0.0, 1.0].")

        # 3. Severity & Event Type
        if event.severity not in VALID_SEVERITIES:
            errors.append(f"Severity '{event.severity}' is invalid. Allowed: {sorted(list(VALID_SEVERITIES))}.")

        # 4. Mandatory descriptive attributes
        if not event.title or len(event.title.strip()) < 3:
            errors.append("Title must be at least 3 characters long.")
        if not event.country or len(event.country.strip()) < 2:
            errors.append("Country specification is required.")
        if not event.region or len(event.region.strip()) < 2:
            errors.append("Region specification is required.")

        return (len(errors) == 0, errors)

    @classmethod
    def validate_raw_dict(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Pre-validation on raw dictionary input prior to Pydantic instantiation."""
        errors: List[str] = []
        required_fields = ["title", "country", "region", "latitude", "longitude"]
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing mandatory field '{field}'.")

        try:
            lat = float(data.get("latitude", 0))
            if not (-90.0 <= lat <= 90.0):
                errors.append(f"Invalid latitude value: {lat}")
        except (ValueError, TypeError):
            errors.append("Latitude must be a valid float.")

        try:
            lon = float(data.get("longitude", 0))
            if not (-180.0 <= lon <= 180.0):
                errors.append(f"Invalid longitude value: {lon}")
        except (ValueError, TypeError):
            errors.append("Longitude must be a valid float.")

        if "confidence" in data and data["confidence"] is not None:
            try:
                conf = float(data["confidence"])
                if not (0.0 <= conf <= 1.0):
                    errors.append(f"Confidence {conf} out of bounds [0.0, 1.0].")
            except (ValueError, TypeError):
                errors.append("Confidence must be a valid float.")

        return (len(errors) == 0, errors)
