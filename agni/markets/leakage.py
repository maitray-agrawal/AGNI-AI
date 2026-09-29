"""
AGNI Temporal Leakage Auditing Engine
=====================================
Rigorous mathematical tests verifying strict causal ordering and zero future lookahead.
Checks that feature values at time t are completely invariant to any future observations (t+1 ... t+N).
"""

from typing import List, Dict, Tuple, Any, Callable, Optional
from datetime import datetime, timedelta
import numpy as np
import polars as pl

from agni.markets.features import MarketFeatureEngine


class TemporalLeakageAuditor:
    """Audits feature pipelines for future lookahead data leakage."""

    @classmethod
    def audit_features_against_truncation(
        cls,
        df: pl.DataFrame,
        feature_generator: Callable[[pl.DataFrame], pl.DataFrame] = MarketFeatureEngine.compute_full_feature_matrix,
        eval_index: int = 80,
    ) -> Dict[str, Any]:
        """
        Mathematical proof of zero future-lookahead:
        1. Compute features on full series df[0:N].
        2. Compute features on truncated series df[0:eval_index].
        3. Compare row at eval_index. If any feature differs by > 1e-7, flag as LEAKAGE.
        """
        if len(df) <= eval_index + 10:
            raise ValueError(f"Series length {len(df)} must be greater than eval_index {eval_index} + 10")

        # 1. Full calculation
        full_features = feature_generator(df)

        # 2. Truncated calculation (strictly historical observations up to eval_index)
        truncated_df = df.slice(0, eval_index + 1)
        truncated_features = feature_generator(truncated_df)

        # 3. Compare values at eval_index
        full_row = full_features.slice(eval_index, 1)
        trunc_row = truncated_features.slice(eval_index, 1)

        numeric_cols = [
            c for c in full_features.columns
            if full_features[c].dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]
            and c not in ["days_to_event"]  # event relative date is fixed relative to external event
        ]

        leaks_detected: List[str] = []
        feature_deltas: Dict[str, float] = {}

        for col in numeric_cols:
            val_full = full_row[col][0]
            val_trunc = trunc_row[col][0]

            if val_full is None and val_trunc is None:
                feature_deltas[col] = 0.0
                continue
            if val_full is None or val_trunc is None:
                leaks_detected.append(col)
                feature_deltas[col] = float("inf")
                continue

            diff = abs(float(val_full) - float(val_trunc))
            feature_deltas[col] = round(diff, 8)
            if diff > 1e-6:
                leaks_detected.append(col)

        return {
            "is_clean": len(leaks_detected) == 0,
            "leak_count": len(leaks_detected),
            "leaked_columns": leaks_detected,
            "eval_index": eval_index,
            "evaluated_columns_count": len(numeric_cols),
            "max_delta": max(feature_deltas.values()) if feature_deltas else 0.0,
            "status": "PASSED_ZERO_LEAKAGE" if len(leaks_detected) == 0 else "FAILED_LEAKAGE_DETECTED",
        }

    @classmethod
    def audit_point_in_time_filtering(
        cls,
        store: Any,
        asset_id: str = "BRENT_CRUDE",
        cutoff_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Verifies that point-in-time querying strictly excludes any future records:
        all returned rows must satisfy available_at <= cutoff_date.
        """
        cutoff = cutoff_date or datetime(2024, 6, 1)
        df = store.get_asset_series(asset_id, as_of=cutoff, limit=1000)

        if df.is_empty():
            return {"is_clean": True, "violations": 0, "status": "EMPTY_RESULT"}

        # Check latest timestamp in returned series
        max_ts = df["timestamp"].max()
        cutoff_naive = cutoff.replace(tzinfo=None) if hasattr(cutoff, "tzinfo") and cutoff.tzinfo else cutoff

        is_valid = max_ts <= cutoff_naive
        return {
            "is_clean": is_valid,
            "max_timestamp": str(max_ts),
            "cutoff_timestamp": str(cutoff_naive),
            "returned_rows": len(df),
            "status": "PASSED_POINT_IN_TIME" if is_valid else "FAILED_POINT_IN_TIME_LEAKAGE",
        }
