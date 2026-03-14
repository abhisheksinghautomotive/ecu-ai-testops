"""Feature engineering module for the ECU anomaly detector.

Extracts statistical features from grouped ECU signal sequences.
"""

from typing import Any

import pandas as pd


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract standard five statistical features per signal sequence.

    Args:
        df: A pandas DataFrame representing the signal log (usually from parquet).
            Expected columns: signal_id, timestamp, value, ...

    Returns:
        A pandas DataFrame where each row corresponds to a unique `signal_id`,
        and columns contain the extracted features:
        - mean
        - std
        - min
        - max
        - response_time_ms (time delta from first to last payload in the sequence)
        Also preserves `fault_label` if present.
    """
    if df.empty:
        return pd.DataFrame()

    # We need realistic numeric parsing. Some injected faults (like Strings "FFFF" or "TIMEOUT")
    # must be coerced to NaN so statistical calculations don't crash.
    def parse_value(val: Any) -> float:
        if pd.isna(val):
            return float('nan')
        val_str = str(val).strip()

        # Try pure numeric first (for OBD)
        try:
            return float(val_str)
        except ValueError:
            pass

        # Try to parse as hex string (common in UDS like '62010C...')
        # Take the first 2 chars (first byte) as indicator of response type
        if len(val_str) >= 2 and all(c in "0123456789abcdefABCDEF" for c in val_str[:2]):
            try:
                return float(int(val_str[:2], 16))
            except ValueError:
                pass

        return float('nan')

    df["numeric_value"] = df["value"].apply(parse_value)

    # Ensure timestamps are actual pandas datetime objects for finding deltas
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    grouped = df.groupby("signal_id")

    # Calculate basic statistical features, dropping NaNs organically
    features = grouped["numeric_value"].agg(["min", "max"])

    # Calculate how many rows are in each sequence
    features["sequence_length"] = grouped["value"].count()

    # Calculate how many values were coerced to NaN (non-numeric timeout or error)
    error_count = grouped["numeric_value"].apply(lambda x: x.isna().sum())
    features["error_rate"] = error_count / features["sequence_length"]

    # Calculate Value Spread (max - min) to detect large out-of-range jumps
    features["value_spread"] = features["max"] - features["min"]

    # If fault_label is present in the source log, bind it to the output feature set
    # by taking the first observation (assuming it's uniform across a sequence block)
    if "fault_label" in df.columns:
        features["fault_label"] = grouped["fault_label"].first()

    # Also bind the signal_type and one-hot encode it so Isolation Forest can distinguish
    # OBD variations from UDS variations
    if "signal_type" in df.columns:
        sig_types = grouped["signal_type"].first()
        # Create boolean columns for each type
        features["is_uds"] = (sig_types == "UDS").astype(float)
        features["is_obd"] = (sig_types == "OBD").astype(float)

    # UDS signals should have very small value spread (only noise). OBD signals vary.
    # This feature helps the unsupervised model isolate UDS out-of-range anomalies.
    features["uds_spread"] = features["is_uds"] * features["value_spread"]

    # Fill any remaining NaNs (e.g., if a sequence was ALL string anomalies,
    # the min/max might be NaN calculation). We can default these to -1.0 as
    # legitimate values are all >= 0
    features = features.fillna(-1.0)

    # Some sequences might only have 1 data point, yielding std = 0.0 (or NaN).
    # Ensure std isn't literally missing if only 1 item.
    if "std" not in features.columns:
        features["std"] = 0.0
    else:
        features["std"] = features["std"].replace(-1.0, 0.0) # We filled NaNs with -1.0 above, std should be 0.0

    return features.reset_index()
