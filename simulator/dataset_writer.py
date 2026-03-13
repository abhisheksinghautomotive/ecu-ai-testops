"""Dataset writer — serialises signal sequences to Parquet format.

Produces a Parquet file with columns:
    signal_id, timestamp, value, signal_type, service_id, fault_label
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

PARQUET_SCHEMA_COLUMNS = [
    "signal_id",
    "timestamp",
    "value",
    "signal_type",
    "service_id",
    "fault_label",
]


def write_parquet(
    sequences: list[dict[str, Any]],
    output_path: str,
) -> str:
    """Write signal sequences to a Parquet file.

    Parameters
    ----------
    sequences:
        List of signal dicts, each containing the schema columns.
    output_path:
        **File path** (not directory) where the ``.parquet`` file will
        be written. Parent directories are created automatically.

    Returns
    -------
    str:
        The absolute path of the written file.

    Raises
    ------
    ValueError:
        If *sequences* is empty or missing required columns.
    """
    if not sequences:
        raise ValueError("Cannot write an empty sequence list to Parquet.")

    df = pd.DataFrame(sequences)

    # Validate required columns are present
    missing = set(PARQUET_SCHEMA_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Keep only the schema columns in canonical order
    df = df[PARQUET_SCHEMA_COLUMNS]

    # Ensure parent directory exists
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(path, index=False, engine="pyarrow")

    return str(path.resolve())
