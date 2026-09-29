"""
AGNI Event Ingestion Service
============================
Handles incoming automated streaming telemetry and analyst workbench payloads.
Applies rigorous validation, coordinate bounds checking, and canonical normalization.
"""

from typing import Dict, Any, List, Union
from agni.data.schemas import Event
from agni.events.validation import EventValidator, ValidationError
from agni.events.normalization import EventNormalizer


class EventIngestionService:
    """Ingests, validates, and normalizes events for the AGNI engine."""

    @classmethod
    def ingest(cls, payload: Union[Dict[str, Any], Event]) -> Event:
        """
        Ingests a single event payload (dictionary or Pydantic model).
        Performs validation, normalization, and returns a verified Event instance.
        """
        if isinstance(payload, dict):
            # Pre-validation on raw dict
            is_valid, errors = EventValidator.validate_raw_dict(payload)
            if not is_valid:
                raise ValidationError(f"Raw event validation failed: {'; '.join(errors)}")

            # Normalize raw fields prior to instantiation
            clean_dict = EventNormalizer.normalize_raw_dict(payload)
            event = Event(**clean_dict)
        elif isinstance(payload, Event):
            event = payload
        else:
            raise ValidationError(f"Unsupported event payload type: {type(payload)}")

        # Strict semantic validation
        is_valid, errors = EventValidator.validate_event(event)
        if not is_valid:
            raise ValidationError(f"Event validation failed: {'; '.join(errors)}")

        # Canonical normalization
        normalized_event = EventNormalizer.normalize_event(event)
        return normalized_event

    @classmethod
    def ingest_batch(cls, items: List[Union[Dict[str, Any], Event]]) -> List[Event]:
        """Ingests a collection of event records, failing fast on invalid entities."""
        return [cls.ingest(item) for item in items]
