"""
AGNI Intelligence Repository & In-Memory / Columnar Store
=========================================================
Stores canonical events, risk signals, scenarios, and forecasts.
Pre-populated with deterministic seed data and supports full manual CRUD.
"""

from typing import List, Optional, Dict
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


class IntelStore:
    def __init__(self):
        self._events: Dict[str, Event] = {e.event_id: e for e in DEMO_EVENTS}
        self._signals: Dict[str, RiskSignal] = {s.signal_id: s for s in DEMO_RISK_SIGNALS}
        self._chokepoints: Dict[str, Chokepoint] = {c.chokepoint_id: c for c in DEMO_CHOKEPOINTS}
        self._countries: Dict[str, Country] = {c.country_code: c for c in DEMO_COUNTRIES}
        self._commodities: Dict[str, Commodity] = {c.commodity_id: c for c in DEMO_COMMODITIES}
        self._assets: Dict[str, FinancialAsset] = {a.asset_id: a for a in DEMO_ASSETS}
        self._regime: RegimeState = DEMO_REGIME_STATE
        self._scenarios: Dict[str, Scenario] = {s.scenario_id: s for s in DEMO_SCENARIOS}
        self._forecasts: Dict[str, Forecast] = {f.forecast_id: f for f in DEMO_FORECASTS}
        self._backtests: List[BacktestResult] = list(DEMO_BACKTESTS)

    # ── Events CRUD ──────────────────────────────────────────────────────────
    def list_events(self) -> List[Event]:
        return list(self._events.values())

    def get_event(self, event_id: str) -> Optional[Event]:
        return self._events.get(event_id)

    def create_event(self, event: Event) -> Event:
        self._events[event.event_id] = event
        # Automatically generate and store risk signal
        sig = risk_signal_engine.evaluate_event(event, current_regime=self._regime.current_regime)
        self._signals[sig.signal_id] = sig
        return event

    def update_event(self, event_id: str, updated_event: Event) -> Optional[Event]:
        if event_id not in self._events:
            return None
        self._events[event_id] = updated_event
        sig = risk_signal_engine.evaluate_event(updated_event, current_regime=self._regime.current_regime)
        self._signals[sig.signal_id] = sig
        return updated_event

    def delete_event(self, event_id: str) -> bool:
        if event_id in self._events:
            del self._events[event_id]
            sig_id = f"sig-{event_id}"
            if sig_id in self._signals:
                del self._signals[sig_id]
            return True
        return False

    # ── Signals ──────────────────────────────────────────────────────────────
    def list_signals(self) -> List[RiskSignal]:
        return list(self._signals.values())

    def get_signal(self, signal_id: str) -> Optional[RiskSignal]:
        return self._signals.get(signal_id)

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
