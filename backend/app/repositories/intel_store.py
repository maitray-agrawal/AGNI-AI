"""
AGNI Intelligence Repository & Analytical In-Memory / Columnar Store
====================================================================
Stores canonical events, risk signals, scenarios, and forecasts.
Pre-populated with deterministic seed data covering all 12 global signal field
hotspots and supports strict manual analyst CRUD workflows.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from backend.app.schemas.canonical import (
    Event,
    RiskSignal,
    Chokepoint,
    Country,
    Commodity,
    FinancialAsset,
    RegimeState,
    Scenario,
    Forecast,
    BacktestResult,
    Evidence,
    EventIntelligenceResult,
)
from backend.app.services.demo_data import (
    DEMO_COUNTRIES,
    DEMO_CHOKEPOINTS,
    DEMO_COMMODITIES,
    DEMO_ASSETS,
    DEMO_EVENTS,
    DEMO_RISK_SIGNALS,
    DEMO_REGIME_STATE,
    DEMO_SCENARIOS,
    DEMO_FORECASTS,
    DEMO_BACKTESTS,
)
from backend.app.services.risk_engine import risk_signal_engine


# Canonical definitions for all 12 Global Signal Field nodes
GLOBAL_SIGNAL_SEEDS = [
    {
        "id": "taiwan-strait",
        "event_id": "taiwan-strait",
        "title": "Taiwan Strait / East Asia Chokepoint",
        "description": "High-density naval patrols & semiconductor export scrutiny. 48% of global container capacity traverses this corridor.",
        "country": "Taiwan / China",
        "region": "East Asia",
        "latitude": 24.0,
        "longitude": 119.5,
        "severity": "critical",
        "confidence": 0.92,
        "affected_assets": ["SPX", "VIX", "DXY"],
        "affected_commodities": ["CONTAINER_SCFI", "COPPER"],
        "affected_routes": ["Trans-Pacific High-Tech Lane", "Taiwan Strait"],
        "transmission_channels": [
            "Naval Corridor Maneuvers",
            "Advanced Wafer Lead Time Escalation",
            "Technology Equity Multiple Contagion",
            "CBOE VIX Volatility Spike",
        ],
    },
    {
        "id": "red-sea-mandeb",
        "event_id": "red-sea-mandeb",
        "title": "Bab el-Mandeb / Southern Red Sea",
        "description": "Commercial vessel rerouting around Cape of Good Hope. Persistent anti-ship missile telemetry and asymmetric maritime drone probes.",
        "country": "Yemen / Djibouti",
        "region": "Middle East & Horn of Africa",
        "latitude": 12.6,
        "longitude": 43.3,
        "severity": "critical",
        "confidence": 0.96,
        "affected_assets": ["VIX", "US10Y"],
        "affected_commodities": ["BRENT_CRUDE", "TTF_GAS", "CONTAINER_SCFI"],
        "affected_routes": ["Bab el-Mandeb", "Asia-Europe Lane"],
        "transmission_channels": [
            "Anti-Ship Ballistic Interdiction",
            "Cape of Good Hope Diversion (+14 Days)",
            "Container Spot Rate Escalation (+110%)",
            "European Import Surcharge Contagion",
        ],
    },
    {
        "id": "strait-hormuz",
        "event_id": "strait-hormuz",
        "title": "Strait of Hormuz",
        "description": "Hydrocarbon transit monitoring & electronic spoofing clusters. 21 million barrels/day flow rate under elevated alert.",
        "country": "Iran / Oman",
        "region": "Persian Gulf",
        "latitude": 26.6,
        "longitude": 56.3,
        "severity": "critical",
        "confidence": 0.94,
        "affected_assets": ["BRENT", "SPX", "US10Y"],
        "affected_commodities": ["BRENT_CRUDE", "TTF_GAS"],
        "affected_routes": ["Strait of Hormuz", "Persian Gulf Tanker Route"],
        "transmission_channels": [
            "GPS Telemetry Spoofing Clusters",
            "Tanker War-Risk Hull Premiums (+35 bps)",
            "Prompt Brent Crude Prompt Spreads",
            "Global Headline Inflation Resurgence",
        ],
    },
    {
        "id": "black-sea-danube",
        "event_id": "black-sea-danube",
        "title": "Black Sea / Danube Grain Corridor",
        "description": "Port infrastructure strikes & agricultural insurance repricing along western Black Sea ports.",
        "country": "Ukraine / Romania",
        "region": "Eastern Europe",
        "latitude": 45.2,
        "longitude": 30.5,
        "severity": "high",
        "confidence": 0.90,
        "affected_assets": ["SPX", "US10Y"],
        "affected_commodities": ["WHEAT", "TTF_GAS"],
        "affected_routes": ["Danube River Corridor", "Black Sea Transit"],
        "transmission_channels": [
            "Grain Terminal Drone Strikes",
            "Bulk Cargo Vessel War-Risk Rating",
            "CBOT Wheat Futures Spike",
            "MENA Food Subsidy Fiscal Strain",
        ],
    },
    {
        "id": "south-china-sea",
        "event_id": "south-china-sea",
        "title": "Second Thomas Shoal / Spratly Islands",
        "description": "Coast guard water cannon encounters & acoustic disruption during resupply missions.",
        "country": "Philippines / China",
        "region": "South China Sea",
        "latitude": 9.8,
        "longitude": 115.8,
        "severity": "high",
        "confidence": 0.88,
        "affected_assets": ["SPX", "VIX"],
        "affected_commodities": ["CONTAINER_SCFI", "COPPER"],
        "affected_routes": ["South China Sea Main Line"],
        "transmission_channels": [
            "Maritime Militia Interdiction",
            "Treaty Consultation Activation",
            "Intra-Asia Freight Routing Hesitation",
            "Regional Equity Risk Premium Expansion",
        ],
    },
    {
        "id": "malacca-strait",
        "event_id": "malacca-strait",
        "title": "Strait of Malacca / Singapore Roads",
        "description": "Bunkering congestion & transshipment container pileup. Container yard utilization exceeds 88%.",
        "country": "Singapore / Malaysia / Indonesia",
        "region": "Southeast Asia",
        "latitude": 1.3,
        "longitude": 103.8,
        "severity": "elevated",
        "confidence": 0.92,
        "affected_assets": ["BRENT", "DXY"],
        "affected_commodities": ["BRENT_CRUDE", "CONTAINER_SCFI"],
        "affected_routes": ["Strait of Malacca"],
        "transmission_channels": [
            "Transshipment Terminal Queue Delays",
            "Feeder Vessel Schedule Slippage",
            "Bunker Fuel Spot Premiums",
            "Manufacturing Component Shortages",
        ],
    },
    {
        "id": "baltic-suwalki",
        "event_id": "baltic-suwalki",
        "title": "Baltic Sea / Suwalki Gap Corridor",
        "description": "Undersea telecom cable anomaly & enhanced border surveillance. Acoustic survey vessels deployed.",
        "country": "Poland / Lithuania / Baltic States",
        "region": "Northern Europe",
        "latitude": 54.3,
        "longitude": 23.2,
        "severity": "high",
        "confidence": 0.89,
        "affected_assets": ["US10Y", "SPX"],
        "affected_commodities": ["TTF_GAS"],
        "affected_routes": ["Baltic Sea Sea-Lanes"],
        "transmission_channels": [
            "Undersea Infrastructure Severance",
            "Air Defense Rotation Activation",
            "Regional Power Grid Decoupling Costs",
            "Sovereign Defense Bond Issuance Pressure",
        ],
    },
    {
        "id": "panama-canal",
        "event_id": "panama-canal",
        "title": "Panama Canal Transit Zone",
        "description": "Draft restrictions & auction slot pricing normalization. Lake Gatun levels monitored.",
        "country": "Panama",
        "region": "Central America",
        "latitude": 9.1,
        "longitude": -79.6,
        "severity": "elevated",
        "confidence": 0.94,
        "affected_assets": ["SPX"],
        "affected_commodities": ["WHEAT", "COPPER"],
        "affected_routes": ["Panama Canal"],
        "transmission_channels": [
            "Freshwater Hydrographic Controls",
            "Neopanamax Transit Slot Auctions",
            "US Gulf to Asia LNG Transit Costs",
            "Agricultural Bulk Freight Rescheduling",
        ],
    },
    {
        "id": "gulf-of-guinea",
        "event_id": "gulf-of-guinea",
        "title": "Gulf of Guinea Maritime Zone",
        "description": "Offshore crude loading security & boarding attempts. Armed security escorts deployed for FPSO offloading.",
        "country": "Nigeria / Ghana",
        "region": "West Africa",
        "latitude": 4.5,
        "longitude": 4.2,
        "severity": "elevated",
        "confidence": 0.87,
        "affected_assets": ["BRENT"],
        "affected_commodities": ["BRENT_CRUDE"],
        "affected_routes": ["West Africa Crude Export Lane"],
        "transmission_channels": [
            "Deepwater FPSO Security Alerts",
            "Crude Cargo Loading Delays",
            "Light Sweet Crude Physical Premiums",
            "Refinery Feedstock Adjustment",
        ],
    },
    {
        "id": "suez-canal",
        "event_id": "suez-canal",
        "title": "Suez Canal Northern Approach",
        "description": "Transit revenue suppression & canal authority tariff concessions. Canal transits down -62% YoY.",
        "country": "Egypt",
        "region": "North Africa",
        "latitude": 31.2,
        "longitude": 32.3,
        "severity": "elevated",
        "confidence": 0.91,
        "affected_assets": ["US10Y", "BRENT"],
        "affected_commodities": ["BRENT_CRUDE", "CONTAINER_SCFI"],
        "affected_routes": ["Suez Canal"],
        "transmission_channels": [
            "Trans-Suez Container Volume Depletion",
            "Egyptian Sovereign FX Reserve Pressure",
            "Mediterranean Bunker Fuel Surplus",
            "Sovereign CDS Spread Widening",
        ],
    },
    {
        "id": "arctic-bering",
        "event_id": "arctic-bering",
        "title": "Bering Strait / Arctic Gateway",
        "description": "Non-ice class cargo convoy monitoring & seasonal ice retreat along the Northern Sea Route.",
        "country": "USA / Russia",
        "region": "Arctic & Polar Corridor",
        "latitude": 65.8,
        "longitude": -168.9,
        "severity": "moderate",
        "confidence": 0.85,
        "affected_assets": ["DXY"],
        "affected_commodities": ["BRENT_CRUDE"],
        "affected_routes": ["Northern Sea Route"],
        "transmission_channels": [
            "Polar Transit Surveillance",
            "Icebreaker Convoy Escort Levies",
            "Alternate Summer Maritime Corridor Testing",
        ],
    },
    {
        "id": "south-asia-vizhinjam",
        "event_id": "south-asia-vizhinjam",
        "title": "Indian Ocean Transshipment Sector",
        "description": "Deepwater transshipment hub capacity absorption. Vizhinjam & Colombo terminals expanding ULCV handling.",
        "country": "India / Sri Lanka",
        "region": "South Asia",
        "latitude": 8.4,
        "longitude": 77.0,
        "severity": "moderate",
        "confidence": 0.88,
        "affected_assets": ["DXY", "SPX"],
        "affected_commodities": ["CONTAINER_SCFI"],
        "affected_routes": ["Indian Ocean Main Line"],
        "transmission_channels": [
            "Indian Ocean Container Flow Redirection",
            "Deepwater Mega-Vessel Berthing Expansion",
            "Regional Feeder Transit Time Reduction",
        ],
    },
]


class IntelStore:
    def __init__(self):
        self._events: Dict[str, Event] = {}
        self._signals: Dict[str, RiskSignal] = {}
        self._chokepoints: Dict[str, Chokepoint] = {c.chokepoint_id: c for c in DEMO_CHOKEPOINTS}
        self._countries: Dict[str, Country] = {c.country_code: c for c in DEMO_COUNTRIES}
        self._commodities: Dict[str, Commodity] = {c.commodity_id: c for c in DEMO_COMMODITIES}
        self._assets: Dict[str, FinancialAsset] = {a.asset_id: a for a in DEMO_ASSETS}
        self._regime: RegimeState = DEMO_REGIME_STATE
        self._scenarios: Dict[str, Scenario] = {s.scenario_id: s for s in DEMO_SCENARIOS}
        self._forecasts: Dict[str, Forecast] = {f.forecast_id: f for f in DEMO_FORECASTS}
        self._backtests: List[BacktestResult] = list(DEMO_BACKTESTS)

        # 1. Populate demo events
        for e in DEMO_EVENTS:
            self._events[e.event_id] = e

        # 2. Populate demo risk signals
        for s in DEMO_RISK_SIGNALS:
            self._signals[s.signal_id] = s

        # 3. Populate all 12 Global Signal Field nodes
        for seed in GLOBAL_SIGNAL_SEEDS:
            ev = Event(
                event_id=seed["event_id"],
                event_type="maritime_disruption",
                title=seed["title"],
                description=seed["description"],
                country=seed["country"],
                region=seed["region"],
                latitude=seed["latitude"],
                longitude=seed["longitude"],
                severity=seed["severity"],
                confidence=seed["confidence"],
                source="AstraX Sovereign Satellite & AIS Monitor",
                affected_assets=seed["affected_assets"],
                affected_commodities=seed["affected_commodities"],
                affected_routes=seed["affected_routes"],
                transmission_channels=seed["transmission_channels"],
                evidence=[
                    Evidence(
                        evidence_id=f"evi-{seed['event_id']}-01",
                        evidence_state="OBSERVED",
                        source_name="AIS Maritime Registry & Multi-Source Intelligence",
                        headline=seed["description"][:120],
                        confidence=seed["confidence"],
                    )
                ],
                is_demo_data=True,
            )
            self._events[ev.event_id] = ev

            # Evaluate signal deterministically
            sig = risk_signal_engine.evaluate_event(ev, current_regime=self._regime.current_regime)
            self._signals[sig.signal_id] = sig
            self._signals[ev.event_id] = sig  # alias direct ID lookup

    # ── Events CRUD ──────────────────────────────────────────────────────────
    def list_events(self) -> List[Event]:
        # Return unique events by event_id
        seen = set()
        res = []
        for e in self._events.values():
            if e.event_id not in seen:
                seen.add(e.event_id)
                res.append(e)
        return res

    def get_event(self, event_id: str) -> Optional[Event]:
        # Flexible key search
        if event_id in self._events:
            return self._events[event_id]
        clean_id = event_id.replace("sig-", "")
        if clean_id in self._events:
            return self._events[clean_id]
        for e in self._events.values():
            if e.event_id == event_id or e.event_id == clean_id:
                return e
        return None

    def create_event(self, event: Event) -> Event:
        self._events[event.event_id] = event
        # Evaluate explainable risk signal
        sig = risk_signal_engine.evaluate_event(event, current_regime=self._regime.current_regime)
        self._signals[sig.signal_id] = sig
        self._signals[event.event_id] = sig
        return event

    def update_event(self, event_id: str, updated_event: Event) -> Optional[Event]:
        if event_id not in self._events and updated_event.event_id not in self._events:
            return None
        self._events[updated_event.event_id] = updated_event
        sig = risk_signal_engine.evaluate_event(updated_event, current_regime=self._regime.current_regime)
        self._signals[sig.signal_id] = sig
        self._signals[updated_event.event_id] = sig
        return updated_event

    def delete_event(self, event_id: str) -> bool:
        found = False
        if event_id in self._events:
            del self._events[event_id]
            found = True
        sig_id = f"sig-{event_id}"
        if sig_id in self._signals:
            del self._signals[sig_id]
        if event_id in self._signals:
            del self._signals[event_id]
        return found

    # ── Signals ──────────────────────────────────────────────────────────────
    def list_signals(self) -> List[RiskSignal]:
        seen = set()
        res = []
        for s in self._signals.values():
            if s.signal_id not in seen:
                seen.add(s.signal_id)
                res.append(s)
        return res

    def get_signal(self, signal_id: str) -> Optional[RiskSignal]:
        # Direct match
        if signal_id in self._signals:
            return self._signals[signal_id]
        # Try with sig- prefix
        prefixed = f"sig-{signal_id}"
        if prefixed in self._signals:
            return self._signals[prefixed]
        # Try without sig- prefix
        unprefixed = signal_id.replace("sig-", "")
        if unprefixed in self._signals:
            return self._signals[unprefixed]
        # Search by event_id
        for s in self._signals.values():
            if s.event_id == signal_id or s.event_id == unprefixed:
                return s
        return None

    def get_event_intelligence(self, event_id: str) -> Optional[EventIntelligenceResult]:
        evt = self.get_event(event_id)
        if not evt:
            return None
        sig = self.get_signal(event_id)
        if not sig:
            sig = risk_signal_engine.evaluate_event(evt, current_regime=self._regime.current_regime)
            self._signals[sig.signal_id] = sig

        return EventIntelligenceResult(
            event_id=evt.event_id,
            title=evt.title,
            risk_score=sig.risk_score,
            risk_level=sig.risk_level,
            confidence=sig.confidence,
            components=sig.components,
            drivers=sig.drivers,
            affected_assets=sig.affected_assets,
            affected_commodities=sig.affected_commodities,
            affected_routes=evt.affected_routes,
            transmission_path=sig.transmission_path,
            epistemic_state="DERIVED",
            calculated_at=sig.timestamp,
        )

    # ── Geopolitical Entities ────────────────────────────────────────────────
    def list_chokepoints(self) -> List[Chokepoint]:
        return list(self._chokepoints.values())

    def list_countries(self) -> List[Country]:
        return list(self._countries.values())

    def list_commodities(self) -> List[Commodity]:
        return list(self._commodities.values())

    def list_assets(self) -> List[FinancialAsset]:
        return list(self._assets.values())

    # ── Regimes ──────────────────────────────────────────────────────────────
    def get_regime_state(self) -> RegimeState:
        return self._regime

    def set_regime_state(self, state: RegimeState):
        self._regime = state

    # ── Scenarios ────────────────────────────────────────────────────────────
    def list_scenarios(self) -> List[Scenario]:
        return list(self._scenarios.values())

    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        return self._scenarios.get(scenario_id)

    def create_scenario(self, scenario: Scenario) -> Scenario:
        self._scenarios[scenario.scenario_id] = scenario
        return scenario

    # ── Forecasts & Backtests ────────────────────────────────────────────────
    def list_forecasts(self) -> List[Forecast]:
        return list(self._forecasts.values())

    def list_backtests(self) -> List[BacktestResult]:
        return self._backtests


intel_store = IntelStore()
