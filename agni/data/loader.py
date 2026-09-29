"""
AGNI Deterministic Dataset Loader
=================================
Loads canonical demo datasets from `datasets/demo/` with schema validation.
"""

import os
import json
from pathlib import Path
from typing import List

from backend.app.schemas.canonical import (
    Event,
    Country,
    Commodity,
    FinancialAsset,
    TradeRoute,
    MarketObservation,
    MacroObservation,
)


def get_demo_dir() -> Path:
    """Returns absolute path to datasets/demo directory."""
    return Path(__file__).resolve().parent.parent.parent / "datasets" / "demo"


def load_demo_events() -> List[Event]:
    path = get_demo_dir() / "events.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Event(**item) for item in data]


def load_demo_countries() -> List[Country]:
    path = get_demo_dir() / "countries.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Country(**item) for item in data]


def load_demo_commodities() -> List[Commodity]:
    path = get_demo_dir() / "commodities.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Commodity(**item) for item in data]


def load_demo_assets() -> List[FinancialAsset]:
    path = get_demo_dir() / "financial_assets.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [FinancialAsset(**item) for item in data]


def load_demo_routes() -> List[TradeRoute]:
    path = get_demo_dir() / "trade_routes.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [TradeRoute(**item) for item in data]


def load_demo_market_observations() -> List[MarketObservation]:
    path = get_demo_dir() / "market_observations.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [MarketObservation(**item) for item in data]


def load_demo_macro_observations() -> List[MacroObservation]:
    path = get_demo_dir() / "macro_observations.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [MacroObservation(**item) for item in data]
