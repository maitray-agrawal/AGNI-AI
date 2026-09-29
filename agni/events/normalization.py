"""
AGNI Event Normalization Engine
===============================
Standardizes event structures, geographic precision, timestamps, and asset tickers.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
import re

from agni.data.schemas import Event


class EventNormalizer:
    """Normalizes raw and semi-structured event inputs into clean canonical forms."""

    @classmethod
    def normalize_event(cls, event: Event) -> Event:
        """Applies canonical normalization rules to an Event model in-place and returns it."""
        # 1. ID normalization
        if not event.event_id or not event.event_id.strip():
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', event.title.lower())[:24].strip('-')
            event.event_id = f"evt-{slug}-{uuid.uuid4().hex[:6]}"

        # 2. Timestamp normalization
        if not event.timestamp:
            event.timestamp = datetime.now(timezone.utc).isoformat()
        else:
            try:
                # Ensure ISO-8601 formatting
                dt = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
                event.timestamp = dt.isoformat()
            except Exception:
                event.timestamp = datetime.now(timezone.utc).isoformat()

        # 3. Coordinate precision normalization (4 decimal places ~ 11 meters)
        event.latitude = round(float(event.latitude), 4)
        event.longitude = round(float(event.longitude), 4)

        # 4. Text trimming and title casing
        event.title = event.title.strip()
        event.country = event.country.strip()
        event.region = event.region.strip()

        # 5. Asset and commodity ticker uppercase standardizations
        event.affected_assets = [
            re.sub(r'[^A-Z0-9_\-]', '', a.strip().upper())
            for a in event.affected_assets if a and a.strip()
        ]
        event.affected_commodities = [
            re.sub(r'[^A-Z0-9_\-]', '', c.strip().upper())
            for c in event.affected_commodities if c and c.strip()
        ]
        event.affected_routes = [
            r.strip() for r in event.affected_routes if r and r.strip()
        ]
        event.transmission_channels = [
            ch.strip() for ch in event.transmission_channels if ch and ch.strip()
        ]

        return event

    @classmethod
    def normalize_raw_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a raw dictionary before instantiation."""
        clean = dict(data)
        if not clean.get("event_id"):
            title = clean.get("title", "event")
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower())[:24].strip('-')
            clean["event_id"] = f"evt-{slug}-{uuid.uuid4().hex[:6]}"

        if not clean.get("timestamp"):
            clean["timestamp"] = datetime.now(timezone.utc).isoformat()

        if not clean.get("event_type"):
            clean["event_type"] = "geopolitical_escalation"

        if not clean.get("description"):
            clean["description"] = clean.get("title", "Geopolitical observation")

        if "latitude" in clean:
            clean["latitude"] = round(float(clean["latitude"]), 4)
        if "longitude" in clean:
            clean["longitude"] = round(float(clean["longitude"]), 4)

        if "confidence" in clean and clean["confidence"] is not None:
            clean["confidence"] = float(clean["confidence"])
        else:
            clean["confidence"] = 0.85

        return clean
