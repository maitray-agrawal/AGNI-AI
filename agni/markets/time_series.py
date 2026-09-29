"""
AGNI Market & Macro Columnar Store (Polars + DuckDB)
====================================================
High-throughput point-in-time time series storage for asset prices,
commodity curves, trade delays, and macroeconomic indicators.
Guarantees zero future-leakage by enforcing `available_at <= evaluation_time`.
"""

import polars as pl
import duckdb
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


class MarketDataStore:
    """Columnar time series repository backed by DuckDB and Polars."""

    def __init__(self, db_path: str = ":memory:"):
        self.con = duckdb.connect(db_path)
        self._init_tables()
        self._seed_deterministic_history()

    def _init_tables(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS market_observations (
                observation_id VARCHAR PRIMARY KEY,
                asset_id VARCHAR,
                timestamp TIMESTAMP,
                available_at TIMESTAMP,
                price DOUBLE,
                volume DOUBLE,
                realized_vol_30d DOUBLE,
                is_demo_data BOOLEAN
            );
            CREATE INDEX IF NOT EXISTS idx_asset_time ON market_observations (asset_id, timestamp);
        """)

    def _seed_deterministic_history(self, days: int = 500):
        """Generates reproducible geometric Brownian motion historical paths with jumps."""
        np.random.seed(42)
        base_date = datetime(2025, 1, 1)

        assets = {
            "BRENT": (78.0, 0.28, 0.02),
            "CONTAINER_SCFI": (3200.0, 0.45, 0.04),
            "SPX": (5700.0, 0.16, -0.01),
            "US10Y": (4.10, 0.12, 0.005),
        }

        records = []
        for asset, (start_price, annual_vol, drift) in assets.items():
            dt = 1.0 / 252.0
            daily_vol = annual_vol * np.sqrt(dt)
            price = start_price

            for i in range(days):
                curr_time = base_date + timedelta(days=i)
                # Random shock with occasional jump
                jump = np.random.choice([0.0, -0.03, 0.04], p=[0.95, 0.025, 0.025])
                ret = (drift * dt) + (daily_vol * np.random.normal(0, 1)) + jump
                price = max(0.1, price * (1.0 + ret))
                vol_30d = annual_vol * (1.0 + (0.2 * np.sin(i / 15.0)))

                records.append((
                    f"obs-{asset.lower()}-{i}",
                    asset,
                    curr_time,
                    curr_time,  # available_at identical to timestamp for historical daily closes
                    round(float(price), 2),
                    round(float(100000 + (np.random.rand() * 50000)), 0),
                    round(float(vol_30d * 100), 2),
                    True,
                ))

        self.con.executemany("""
            INSERT INTO market_observations VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, records)

    def get_asset_series(
        self,
        asset_id: str,
        as_of: Optional[datetime] = None,
        limit: int = 250,
    ) -> pl.DataFrame:
        """Retrieves point-in-time historical prices, strictly preventing future leakage."""
        cutoff = as_of or datetime.utcnow()
        df = self.con.execute("""
            SELECT timestamp, price, volume, realized_vol_30d
            FROM market_observations
            WHERE asset_id = ? AND available_at <= ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, [asset_id, cutoff, limit]).pl()

        return df.reverse()


market_store = MarketDataStore()
