"""OBD-II PID response sequence generator.

Generates synthetic OBD-II diagnostic responses for common PIDs
(Engine RPM, Coolant Temperature, O2 Sensor voltage) with realistic
Gaussian noise.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

# ── PID definitions ──────────────────────────────────────────────────
# Each PID maps to a name, unit, formula bounds, and typical centre.
PIDS: dict[str, dict[str, Any]] = {
    "0C": {
        "name": "engine_rpm",
        "unit": "RPM",
        "min": 0.0,
        "max": 8000.0,
        "typical_centre": 3000.0,
        "typical_std": 500.0,
    },
    "05": {
        "name": "coolant_temperature",
        "unit": "°C",
        "min": -40.0,
        "max": 215.0,
        "typical_centre": 90.0,
        "typical_std": 10.0,
    },
    "14": {
        "name": "o2_sensor_voltage",
        "unit": "V",
        "min": 0.0,
        "max": 1.275,
        "typical_centre": 0.45,
        "typical_std": 0.15,
    },
}


def _format_obd_value(value: float, pid_key: str) -> str:
    """Format a PID reading as a human-readable string with unit."""
    pid_info = PIDS[pid_key]
    if pid_info["unit"] == "RPM":
        return f"{value:.0f}"
    if pid_info["unit"] == "°C":
        return f"{value:.1f}"
    return f"{value:.3f}"


def generate_obd_sequences(
    n: int = 2500,
    fault_rate: float = 0.0,
    rng_seed: int | None = None,
) -> list[dict[str, Any]]:
    """Generate *n* OBD-II PID response sequences.

    Parameters
    ----------
    n:
        Number of sequences to generate.
    fault_rate:
        Fraction of sequences pre-marked as faults (0.0–1.0).
        Actual fault injection is handled by ``fault_injector``.
    rng_seed:
        Optional seed for reproducibility.

    Returns
    -------
    list[dict]:
        Each dict contains: signal_id, timestamp, value, signal_type,
        service_id, fault_label.
    """
    rng = np.random.default_rng(rng_seed)
    pid_keys = list(PIDS.keys())
    base_time = datetime.now(tz=UTC)

    sequences: list[dict[str, Any]] = []
    for i in range(n):
        pid_key = pid_keys[i % len(pid_keys)]
        pid_info = PIDS[pid_key]
        signal_id = str(uuid.uuid4())

        # Determine a random sequence length between 5 and 20 points
        seq_length = rng.integers(5, 20)

        # Start time for this sequence
        seq_time = base_time + timedelta(seconds=i * 2)

        for j in range(seq_length):
            # Gaussian distribution centred on typical operating value
            raw_value = rng.normal(pid_info["typical_centre"], pid_info["typical_std"])
            value = float(np.clip(raw_value, pid_info["min"], pid_info["max"]))

            formatted = _format_obd_value(value, pid_key)
            timestamp = seq_time + timedelta(milliseconds=j * 100)

            sequences.append(
                {
                    "signal_id": signal_id,
                    "timestamp": timestamp.isoformat(),
                    "value": formatted,
                    "signal_type": "OBD",
                    "service_id": f"0x{pid_key}",
                    "fault_label": False,
                    "sequence_index": i, # Used internally for fault injection tracking
                }
            )

    # Pre-mark faults if requested
    if fault_rate > 0.0:
        n_faults = int(n * fault_rate)
        fault_indices = rng.choice(n, size=n_faults, replace=False)
        fault_seq_set = set(fault_indices)

        for seq in sequences:
            if seq.get("sequence_index") in fault_seq_set:
                seq["fault_label"] = True

    # Clean up internal tracking
    for seq in sequences:
        seq.pop("sequence_index", None)
    if fault_rate > 0.0:
        n_faults = int(n * fault_rate)
        fault_indices = rng.choice(n, size=n_faults, replace=False)
        for idx in fault_indices:
            sequences[int(idx)]["fault_label"] = True

    return sequences
