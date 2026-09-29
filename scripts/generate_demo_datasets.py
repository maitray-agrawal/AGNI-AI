import os
import json
import numpy as np

os.makedirs('datasets/demo', exist_ok=True)
np.random.seed(42)

# 1. Countries
countries = [
    {"country_code": "IRN", "name": "Islamic Republic of Iran", "region": "Middle East", "latitude": 32.4279, "longitude": 53.6880, "gdp_usd_billions": 388.8, "geopolitical_risk_index": 148.5},
    {"country_code": "TWN", "name": "Taiwan", "region": "East Asia", "latitude": 23.6978, "longitude": 120.9605, "gdp_usd_billions": 756.2, "geopolitical_risk_index": 136.2},
    {"country_code": "YEM", "name": "Yemen", "region": "Middle East", "latitude": 15.5527, "longitude": 48.5164, "gdp_usd_billions": 21.6, "geopolitical_risk_index": 182.0},
    {"country_code": "PAN", "name": "Panama", "region": "Latin America", "latitude": 8.5380, "longitude": -80.7821, "gdp_usd_billions": 76.5, "geopolitical_risk_index": 62.4},
    {"country_code": "EGY", "name": "Egypt", "region": "Middle East / North Africa", "latitude": 26.8206, "longitude": 30.8025, "gdp_usd_billions": 398.4, "geopolitical_risk_index": 115.0},
    {"country_code": "SGP", "name": "Singapore", "region": "Southeast Asia", "latitude": 1.3521, "longitude": 103.8198, "gdp_usd_billions": 501.4, "geopolitical_risk_index": 45.0}
]
with open('datasets/demo/countries.json', 'w', encoding='utf-8') as f:
    json.dump(countries, f, indent=2)

# 2. Commodities
commodities = [
    {"commodity_id": "BRENT_CRUDE", "name": "Brent Crude Oil", "category": "Energy", "benchmark_unit": "USD/bbl", "primary_chokepoint_dependencies": ["strait-of-hormuz", "suez-canal"]},
    {"commodity_id": "NATURAL_GAS_TTF", "name": "Dutch TTF Natural Gas", "category": "Energy", "benchmark_unit": "EUR/MWh", "primary_chokepoint_dependencies": ["suez-canal", "bab-el-mandeb"]},
    {"commodity_id": "CONTAINER_SCFI", "name": "Shanghai Containerized Freight Index", "category": "Freight Logistics", "benchmark_unit": "USD/TEU", "primary_chokepoint_dependencies": ["bab-el-mandeb", "suez-canal", "panama-canal"]},
    {"commodity_id": "COPPER_GRADE_A", "name": "LME Copper Grade A", "category": "Industrial Metals", "benchmark_unit": "USD/MT", "primary_chokepoint_dependencies": ["panama-canal", "strait-of-malacca"]},
    {"commodity_id": "WHEAT_MILLING", "name": "Milling Wheat", "category": "Agricultural", "benchmark_unit": "USD/bu", "primary_chokepoint_dependencies": ["bosphorus-strait", "suez-canal"]}
]
with open('datasets/demo/commodities.json', 'w', encoding='utf-8') as f:
    json.dump(commodities, f, indent=2)

# 3. Financial Assets (Conforming to AssetClass Literal)
assets = [
    {"asset_id": "BRENT", "name": "Brent Crude Front Month", "asset_class": "commodity", "currency": "USD", "current_value": 82.45, "daily_change_pct": 1.84},
    {"asset_id": "SPX", "name": "S&P 500 Index", "asset_class": "equity_index", "currency": "USD", "current_value": 5815.20, "daily_change_pct": -0.42},
    {"asset_id": "US10Y", "name": "US 10-Year Treasury Benchmark Yield", "asset_class": "sovereign_bond", "currency": "USD", "current_value": 4.28, "daily_change_pct": 0.05},
    {"asset_id": "VIX", "name": "CBOE Volatility Index", "asset_class": "volatility", "currency": "USD", "current_value": 17.65, "daily_change_pct": 8.20},
    {"asset_id": "DXY", "name": "US Dollar Currency Index", "asset_class": "fx_rate", "currency": "USD", "current_value": 104.12, "daily_change_pct": 0.35}
]
with open('datasets/demo/financial_assets.json', 'w', encoding='utf-8') as f:
    json.dump(assets, f, indent=2)

# 4. Trade Routes
routes = [
    {"route_id": "asia-europe-suez", "name": "Asia to North Europe via Suez Canal", "origin_region": "East Asia", "destination_region": "North Europe", "traversed_chokepoints": ["strait-of-malacca", "bab-el-mandeb", "suez-canal"], "average_transit_days": 28.0, "current_delay_days": 10.5},
    {"route_id": "gulf-asia-tanker", "name": "Persian Gulf to East Asia VLCC Route", "origin_region": "Middle East", "destination_region": "East Asia", "traversed_chokepoints": ["strait-of-hormuz", "strait-of-malacca"], "average_transit_days": 18.0, "current_delay_days": 2.0},
    {"route_id": "transpacific-us-east", "name": "Transpacific Asia to US East Coast via Panama", "origin_region": "East Asia", "destination_region": "US East Coast", "traversed_chokepoints": ["panama-canal"], "average_transit_days": 24.0, "current_delay_days": 6.0}
]
with open('datasets/demo/trade_routes.json', 'w', encoding='utf-8') as f:
    json.dump(routes, f, indent=2)

# 5. Geopolitical Events with explicit canonical Evidence fields
events = [
    {
        "event_id": "evt-demo-001",
        "timestamp": "2026-09-29T08:00:00Z",
        "event_type": "maritime_disruption",
        "title": "Bab el-Mandeb Anti-Ship Drone Strike",
        "description": "Commercial container vessel targeted by unmanned aerial vehicle in the southern Red Sea transit corridor, precipitating commercial rerouting around the Cape of Good Hope.",
        "country": "Yemen",
        "region": "Middle East",
        "latitude": 12.5833,
        "longitude": 43.3333,
        "severity": "critical",
        "confidence": 0.94,
        "source": "AstraX Maritime Stream (AIS Verified)",
        "affected_assets": ["BRENT", "VIX"],
        "affected_commodities": ["CONTAINER_SCFI", "BRENT_CRUDE"],
        "affected_routes": ["asia-europe-suez"],
        "transmission_channels": ["Missile Strike", "Cape Rerouting", "Transit Delay (+12D)", "Bunker Fuel Surcharge"],
        "is_demo_data": True,
        "evidence": [
            {
                "evidence_id": "ev-001-obs",
                "timestamp": "2026-09-29T08:05:00Z",
                "evidence_state": "OBSERVED",
                "source_name": "UKMTO Advisory Notice 041/2026",
                "headline": "Verified kinetic impact coordinate 12.58N, 43.33E",
                "confidence": 0.98,
                "extracted_text": "Vessel struck on port quarter, no casualties reported, vessel continuing at reduced speed.",
                "is_air_gapped": True
            },
            {
                "evidence_id": "ev-001-der",
                "timestamp": "2026-09-29T08:20:00Z",
                "evidence_state": "DERIVED",
                "source_name": "AGNI AIS Kinematic Calculator",
                "headline": "38 commercial vessels executing 180-degree diversion",
                "confidence": 0.92,
                "extracted_text": "Kinematic vector analysis confirms diversion from Red Sea towards Cape of Good Hope route.",
                "is_air_gapped": True
            },
            {
                "evidence_id": "ev-001-mod",
                "timestamp": "2026-09-29T08:30:00Z",
                "evidence_state": "MODELLED",
                "source_name": "AGNI Event-Conditioned Forecaster",
                "headline": "Spot container rates projected +28% over 14-day horizon",
                "confidence": 0.88,
                "is_air_gapped": True
            },
            {
                "evidence_id": "ev-001-sce",
                "timestamp": "2026-09-29T08:45:00Z",
                "evidence_state": "SCENARIO",
                "source_name": "AGNI Stress Engine Severe Run",
                "headline": "Full corridor closure adds $1.8M voyage cost per round-trip",
                "confidence": 0.75,
                "is_air_gapped": True
            }
        ]
    },
    {
        "event_id": "evt-demo-002",
        "timestamp": "2026-09-29T09:15:00Z",
        "event_type": "energy_disruption",
        "title": "Strait of Hormuz Tanker Escort Probes",
        "description": "Naval patrol vessels conduct close intercept maneuvers against commercial Suezmax crude tankers in the outbound traffic separation scheme.",
        "country": "Iran",
        "region": "Middle East",
        "latitude": 26.5667,
        "longitude": 56.2500,
        "severity": "high",
        "confidence": 0.91,
        "source": "AstraX Sovereign Telemetry",
        "affected_assets": ["BRENT", "VIX"],
        "affected_commodities": ["BRENT_CRUDE"],
        "affected_routes": ["gulf-asia-tanker"],
        "transmission_channels": ["Naval Probe", "War Risk Premium (+40bps)", "Brent Prompt Crack Spread Surge"],
        "is_demo_data": True,
        "evidence": [
            {
                "evidence_id": "ev-002-obs",
                "timestamp": "2026-09-29T09:20:00Z",
                "evidence_state": "OBSERVED",
                "source_name": "Joint Maritime Information Center (JMIC)",
                "headline": "Vessel bridge VHF recording confirms intercept warnings",
                "confidence": 0.96,
                "is_air_gapped": True
            },
            {
                "evidence_id": "ev-002-mod",
                "timestamp": "2026-09-29T09:35:00Z",
                "evidence_state": "MODELLED",
                "source_name": "Hamilton Markov Regime Detector",
                "headline": "Energy volatility state shifts from ELEVATED to STRESSED",
                "confidence": 0.86,
                "is_air_gapped": True
            }
        ]
    },
    {
        "event_id": "evt-demo-003",
        "timestamp": "2026-09-29T10:30:00Z",
        "event_type": "natural_hazard",
        "title": "Panama Canal Gatun Lake Draft Restrictions",
        "description": "Panama Canal Authority institutes fresh draft restriction of 43.5 feet following prolonged seasonal watershed precipitation deficits.",
        "country": "Panama",
        "region": "Latin America",
        "latitude": 9.0800,
        "longitude": -79.6800,
        "severity": "elevated",
        "confidence": 0.98,
        "source": "Panama Canal Authority Advisory A-22-2026",
        "affected_assets": ["SPX"],
        "affected_commodities": ["CONTAINER_SCFI", "COPPER_GRADE_A"],
        "affected_routes": ["transpacific-us-east"],
        "transmission_channels": ["Draft Cut", "Slots Reduced", "Auction Slot Premium Surge", "Transit Delay (+6D)"],
        "is_demo_data": True,
        "evidence": [
            {
                "evidence_id": "ev-003-obs",
                "timestamp": "2026-09-29T10:35:00Z",
                "evidence_state": "OBSERVED",
                "source_name": "ACP Official Advisory",
                "headline": "Maximum allowable draft reduction to 43.5 feet Tropical Fresh Water",
                "confidence": 0.99,
                "is_air_gapped": True
            },
            {
                "evidence_id": "ev-003-der",
                "timestamp": "2026-09-29T10:50:00Z",
                "evidence_state": "DERIVED",
                "source_name": "AGNI Canal Queue Model",
                "headline": "Anchorage wait time extends from 48 to 144 hours",
                "confidence": 0.90,
                "is_air_gapped": True
            }
        ]
    }
]
with open('datasets/demo/events.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, indent=2)

# 6. Market Observations
market_obs = []
base_brent = 80.0
for i in range(30):
    day = f'2026-09-{i+1:02d}'
    base_brent += float(np.random.normal(0.08, 0.9))
    market_obs.append({
        "observation_id": f"obs-brent-{day}",
        "asset_id": "BRENT",
        "timestamp": f"{day}T16:30:00Z",
        "available_at": f"{day}T16:35:00Z",
        "price": round(base_brent, 2),
        "volume": round(float(np.random.uniform(180000, 320000)), 0),
        "implied_volatility": round(float(np.random.uniform(0.18, 0.28)), 4),
        "source": "ICE Futures Europe (Verified Settlement)",
        "is_demo_data": True
    })
with open('datasets/demo/market_observations.json', 'w', encoding='utf-8') as f:
    json.dump(market_obs, f, indent=2)

# 7. Macro Observations
macro_obs = [
    {
        "observation_id": "macro-gpr-2026-09",
        "country_code": "GLOBAL",
        "indicator_code": "GPR_INDEX",
        "timestamp": "2026-09-01T00:00:00Z",
        "available_at": "2026-09-02T12:00:00Z",
        "value": 142.8,
        "unit": "points",
        "frequency": "monthly",
        "source": "Federal Reserve Board Research",
        "is_demo_data": True
    },
    {
        "observation_id": "macro-us-cpi-2026-08",
        "country_code": "USA",
        "indicator_code": "CPI_YOY",
        "timestamp": "2026-08-31T23:59:59Z",
        "available_at": "2026-09-11T12:30:00Z",
        "value": 2.85,
        "unit": "percent",
        "frequency": "monthly",
        "source": "US Bureau of Labor Statistics",
        "is_demo_data": True
    },
    {
        "observation_id": "macro-regime-est",
        "country_code": "GLOBAL",
        "indicator_code": "SOVEREIGN_STRESS",
        "timestamp": "2026-09-29T12:00:00Z",
        "available_at": "2026-09-29T12:00:00Z",
        "value": 68.4,
        "unit": "score_0_100",
        "frequency": "daily",
        "source": "AGNI Hamilton Switching Model",
        "is_demo_data": True
    }
]
with open('datasets/demo/macro_observations.json', 'w', encoding='utf-8') as f:
    json.dump(macro_obs, f, indent=2)

print('SUCCESS')
