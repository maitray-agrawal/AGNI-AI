"""
Phase 1 Tests: Deterministic Demo Datasets
==========================================
Validates that all 7 demo datasets in `datasets/demo/` load deterministically,
parse into canonical models, and enforce epistemic state segregation.
"""

import pytest
from agni.data.loader import (
    load_demo_events,
    load_demo_countries,
    load_demo_commodities,
    load_demo_assets,
    load_demo_routes,
    load_demo_market_observations,
    load_demo_macro_observations,
)


def test_load_demo_events():
    events = load_demo_events()
    assert len(events) >= 3
    for evt in events:
        assert evt.is_demo_data is True
        assert evt.severity in ("critical", "high", "elevated", "moderate", "low", "info")
        assert len(evt.evidence) > 0
        # Check evidence contains clear epistemic states
        states = {ev.evidence_state for ev in evt.evidence}
        assert any(s in ("OBSERVED", "DERIVED", "MODELLED", "SCENARIO") for s in states)
        for ev in evt.evidence:
            assert ev.source_name is not None
            assert ev.headline is not None


def test_load_demo_countries():
    countries = load_demo_countries()
    assert len(countries) >= 5
    codes = {c.country_code for c in countries}
    assert "IRN" in codes
    assert "TWN" in codes
    assert "PAN" in codes


def test_load_demo_commodities():
    commodities = load_demo_commodities()
    assert len(commodities) >= 5
    ids = {c.commodity_id for c in commodities}
    assert "BRENT_CRUDE" in ids
    assert "CONTAINER_SCFI" in ids


def test_load_demo_assets():
    assets = load_demo_assets()
    assert len(assets) >= 5
    tickers = {a.asset_id for a in assets}
    assert "BRENT" in tickers
    assert "SPX" in tickers
    assert "VIX" in tickers


def test_load_demo_routes():
    routes = load_demo_routes()
    assert len(routes) >= 3
    for r in routes:
        assert len(r.traversed_chokepoints) > 0
        assert r.average_transit_days > 0


def test_load_demo_market_and_macro_observations():
    mkt = load_demo_market_observations()
    assert len(mkt) == 30
    for obs in mkt:
        assert obs.asset_id == "BRENT"
        assert obs.price > 0
        assert obs.is_demo_data is True

    macro = load_demo_macro_observations()
    assert len(macro) >= 3
    indicators = {m.indicator_code for m in macro}
    assert "GPR_INDEX" in indicators
    for m in macro:
        assert m.value > 0
        assert m.country_code is not None
