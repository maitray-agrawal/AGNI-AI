"""
AGNI Canonical Market & Macro Time Series Store
================================================
High-throughput point-in-time market and macroeconomic analytical repository
powered by Polars, DuckDB, and Apache Parquet.

Covers all core asset classes:
- FX: DXY, EURUSD
- Commodities: BRENT_CRUDE, NATURAL_GAS_TTF, CONTAINER_SCFI, COPPER, WHEAT
- Equities: SPX
- Sovereign Yields: US10Y
- Volatility: VIX
- Macro Indicators: CPI_YOY, FED_FUNDS_RATE, GPR_INDEX, SOVEREIGN_CDS

Guarantees zero future-leakage by enforcing strict point-in-time filters (`available_at <= evaluation_time`).
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple, Any

import numpy as np
import polars as pl
import duckdb

from backend.app.schemas.canonical import MarketObservation, MacroObservation

DEFAULT_PARQUET_DIR = Path("datasets/market")


class MarketDataStore:
    """Analytical time series store backed by DuckDB and Polars with Parquet persistence."""

    def __init__(self, storage_dir: Optional[Path] = None, seed: int = 42):
        self.storage_dir = Path(storage_dir or DEFAULT_PARQUET_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.market_parquet = self.storage_dir / "market_series.parquet"
        self.macro_parquet = self.storage_dir / "macro_series.parquet"

        self.con = duckdb.connect(":memory:")
        self.seed = seed
        self._init_tables()
        self._ensure_datasets()

    def _init_tables(self):
        """Initializes high-performance indexed DuckDB tables."""
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS market_observations (
                observation_id VARCHAR PRIMARY KEY,
                asset_id VARCHAR,
                timestamp TIMESTAMP,
                available_at TIMESTAMP,
                price DOUBLE,
                volume DOUBLE,
                realized_vol_30d DOUBLE,
                asset_class VARCHAR,
                is_demo_data BOOLEAN
            );
            CREATE INDEX IF NOT EXISTS idx_mkt_asset_time ON market_observations (asset_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_mkt_avail ON market_observations (available_at);

            CREATE TABLE IF NOT EXISTS macro_observations (
                observation_id VARCHAR PRIMARY KEY,
                country_code VARCHAR,
                indicator_code VARCHAR,
                timestamp TIMESTAMP,
                available_at TIMESTAMP,
                value DOUBLE,
                source VARCHAR,
                is_demo_data BOOLEAN
            );
            CREATE INDEX IF NOT EXISTS idx_macro_ind_time ON macro_observations (indicator_code, timestamp);
        """)

    def _ensure_datasets(self):
        """Generates deterministic Parquet datasets if not present, then mounts them into DuckDB."""
        if not self.market_parquet.exists() or not self.macro_parquet.exists():
            self._generate_canonical_history()
        else:
            self._load_from_parquet()

    def _generate_canonical_history(self, days: int = 600):
        """
        Generates deterministic, economically calibrated time series for all required assets:
        FX, commodities, equities, yields, volatility, and macro indicators.
        """
        np.random.seed(self.seed)
        start_date = datetime(2024, 1, 1)

        # Assets: (start_price, annual_vol, annual_drift, asset_class)
        ASSET_CONFIGS = {
            # FX
            "DXY": (102.5, 0.08, 0.01, "fx_rate"),
            "EURUSD": (1.085, 0.09, -0.01, "fx_rate"),
            # Commodities
            "BRENT_CRUDE": (77.5, 0.28, 0.03, "commodity"),
            "NATURAL_GAS_TTF": (32.0, 0.48, 0.05, "commodity"),
            "CONTAINER_SCFI": (2100.0, 0.42, 0.06, "commodity"),
            "COPPER": (8900.0, 0.22, 0.02, "commodity"),
            "WHEAT": (580.0, 0.26, 0.01, "commodity"),
            # Equities
            "SPX": (5000.0, 0.16, 0.08, "equity_index"),
            # Yields
            "US10Y": (4.15, 0.14, 0.01, "sovereign_bond"),
            # Volatility
            "VIX": (15.5, 0.55, 0.00, "volatility"),
        }

        market_rows = []
        dt = 1.0 / 252.0

        for asset_id, (s_price, ann_vol, drift, a_class) in ASSET_CONFIGS.items():
            daily_vol = ann_vol * np.sqrt(dt)
            price = s_price
            vol_state = ann_vol

            for i in range(days):
                curr_time = start_date + timedelta(days=i)
                # Occasional geopolitical jump shock
                jump = 0.0
                if np.random.rand() < 0.03:
                    jump = np.random.choice([-0.04, 0.05])

                # Mean reversion for yields and VIX, GBM for equities and commodities
                if a_class == "volatility":
                    price = max(10.0, price + 0.10 * (18.0 - price) * dt + price * daily_vol * np.random.normal(0, 1) + (jump * 15.0))
                elif a_class == "sovereign_bond":
                    price = max(1.5, price + 0.05 * (4.25 - price) * dt + price * daily_vol * np.random.normal(0, 1) + (jump * 0.5))
                else:
                    ret = (drift * dt) + (daily_vol * np.random.normal(0, 1)) + jump
                    price = max(0.5, price * (1.0 + ret))

                # GARCH-style clustering for realized vol
                vol_state = np.sqrt(0.0001 + 0.85 * (vol_state ** 2) + 0.10 * ((price * daily_vol) ** 2))
                realized_vol_30d = round(float(vol_state * 100), 2)

                vol_volume = int(np.random.uniform(50000, 300000))

                market_rows.append({
                    "observation_id": f"obs-{asset_id.lower()}-{i}",
                    "asset_id": asset_id,
                    "timestamp": curr_time,
                    "available_at": curr_time,  # Closing tick available at close
                    "price": round(float(price), 4),
                    "volume": float(vol_volume),
                    "realized_vol_30d": realized_vol_30d,
                    "asset_class": a_class,
                    "is_demo_data": True,
                })

        mkt_df = pl.DataFrame(market_rows)
        mkt_df.write_parquet(self.market_parquet)

        # Generate Macro Observations (monthly indicators)
        MACRO_INDICATORS = {
            "CPI_YOY": ("USA", 3.2, 0.05, "BLS / FRED"),
            "FED_FUNDS_RATE": ("USA", 5.25, -0.05, "Federal Reserve"),
            "GPR_INDEX": ("GLB", 135.0, 1.5, "Caldara & Iacoviello"),
            "SOVEREIGN_CDS": ("EGY", 650.0, 4.0, "Markit Sovereign CDS"),
        }

        macro_rows = []
        months = days // 30
        for ind_code, (country, start_val, trend, src) in MACRO_INDICATORS.items():
            val = start_val
            for m in range(months):
                t_time = start_date + timedelta(days=m * 30)
                # Macro publications have a 15-day reporting lag (strictly enforced point-in-time)
                avail_time = t_time + timedelta(days=15)
                val = max(0.0, val + (trend * np.random.normal(1.0, 0.2)))
                macro_rows.append({
                    "observation_id": f"macro-{ind_code.lower()}-{m}",
                    "country_code": country,
                    "indicator_code": ind_code,
                    "timestamp": t_time,
                    "available_at": avail_time,
                    "value": round(float(val), 2),
                    "source": src,
                    "is_demo_data": True,
                })

        macro_df = pl.DataFrame(macro_rows)
        macro_df.write_parquet(self.macro_parquet)

        self._load_from_parquet()

    def _load_from_parquet(self):
        """Loads Parquet files into in-memory DuckDB tables."""
        mkt_path = str(self.market_parquet).replace("\\", "/")
        macro_path = str(self.macro_parquet).replace("\\", "/")

        self.con.execute(f"DELETE FROM market_observations")
        self.con.execute(f"INSERT INTO market_observations SELECT * FROM read_parquet('{mkt_path}')")

        self.con.execute(f"DELETE FROM macro_observations")
        self.con.execute(f"INSERT INTO macro_observations SELECT * FROM read_parquet('{macro_path}')")

    # ── High-Throughput Point-in-Time Accessors ──────────────────────────────

    def get_asset_series(
        self,
        asset_id: str,
        as_of: Optional[datetime] = None,
        limit: int = 500,
    ) -> pl.DataFrame:
        """
        Retrieves point-in-time historical prices for an asset.
        Guarantees zero future-leakage by filtering `available_at <= cutoff`.
        """
        cutoff = as_of or datetime.now(timezone.utc)
        df = self.con.execute("""
            SELECT timestamp, asset_id, price, volume, realized_vol_30d, asset_class, available_at
            FROM market_observations
            WHERE asset_id = ? AND available_at <= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, [asset_id.upper(), cutoff, limit]).pl()

        return df.reverse()

    def get_cross_asset_series(
        self,
        asset_ids: List[str],
        as_of: Optional[datetime] = None,
        limit: int = 250,
    ) -> pl.DataFrame:
        """Pivots multiple asset price series into a synchronized time-aligned table."""
        cutoff = as_of or datetime.now(timezone.utc)
        placeholders = ", ".join(["?"] * len(asset_ids))
        params = [a.upper() for a in asset_ids] + [cutoff]

        query = f"""
            SELECT timestamp, asset_id, price
            FROM market_observations
            WHERE asset_id IN ({placeholders}) AND available_at <= ?
            ORDER BY timestamp ASC
        """
        raw_df = self.con.execute(query, params).pl()
        if raw_df.is_empty():
            return pl.DataFrame()

        # Pivot to wide format: timestamp | ASSET1 | ASSET2 ...
        wide_df = raw_df.pivot(
            values="price",
            index="timestamp",
            on="asset_id",
            aggregate_function="last"
        ).sort("timestamp").tail(limit)

        return wide_df

    def get_macro_series(
        self,
        indicator_code: str,
        as_of: Optional[datetime] = None,
    ) -> pl.DataFrame:
        """Point-in-time macroeconomic series accessor."""
        cutoff = as_of or datetime.now(timezone.utc)
        df = self.con.execute("""
            SELECT timestamp, available_at, value, country_code, indicator_code, source
            FROM macro_observations
            WHERE indicator_code = ? AND available_at <= ?
            ORDER BY timestamp ASC
        """, [indicator_code.upper(), cutoff]).pl()
        return df

    def get_macro_indicators(
        self,
        as_of: Optional[datetime] = None,
        limit: int = 500,
    ) -> pl.DataFrame:
        """Retrieves point-in-time macro indicator records across all indicators."""
        cutoff = as_of or datetime.now(timezone.utc)
        df = self.con.execute("""
            SELECT timestamp, available_at, country_code, indicator_code, value, source
            FROM macro_observations
            WHERE available_at <= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, [cutoff, limit]).pl()
        return df.reverse()

    def list_available_assets(self) -> List[Dict[str, str]]:
        """Lists all active asset tickers with their asset class."""
        res = self.con.execute("SELECT DISTINCT asset_id, asset_class FROM market_observations ORDER BY asset_id").fetchall()
        return [{"asset_id": r[0], "asset_class": r[1]} for r in res]

    def list_available_asset_ids(self) -> List[str]:
        """Lists asset tickers as string list."""
        res = self.con.execute("SELECT DISTINCT asset_id FROM market_observations ORDER BY asset_id").fetchall()
        return [r[0] for r in res]

    def list_macro_indicators(self) -> List[str]:
        """Lists all active macroeconomic indicators."""
        res = self.con.execute("SELECT DISTINCT indicator_code FROM macro_observations ORDER BY indicator_code").fetchall()
        return [r[0] for r in res]


# Global singleton instance
market_data_store = MarketDataStore()
