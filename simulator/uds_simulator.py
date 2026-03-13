"""UDS Service 0x22 (ReadDataByIdentifier) signal sequence generator.

Generates synthetic UDS diagnostic response sequences mimicking real ECU
responses for configurable Data Identifiers (DIDs).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np

# ── DID definitions ──────────────────────────────────────────────────
# Each DID maps to a human-readable name, a normal value range, and a
# response byte length (excluding the positive-response prefix 0x62).
DIDS: dict[str, dict[str, Any]] = {
    "F1A0": {
        "name": "coolant_temperature",
        "unit": "°C",
        "min": -40.0,
        "max": 215.0,
        "byte_length": 2,
    },
    "F1A1": {
        "name": "engine_rpm",
        "unit": "RPM",
        "min": 600.0,
        "max": 7000.0,
        "byte_length": 2,
    },
    "F1A2": {
        "name": "battery_voltage",
        "unit": "V",
        "min": 11.5,
        "max": 14.8,
        "byte_length": 2,
    },
}

UDS_SERVICE_ID = "0x22"
POSITIVE_RESPONSE_SID = "62"


def _encode_value_hex(value: float, byte_length: int) -> str:
    """Encode a float value as a hex string with the given byte length.

    The value is scaled to an unsigned integer that fits in *byte_length*
    bytes (0 – 2^(8*byte_length)-1), then zero-padded to the correct
    width.
    """
    max_int = (1 << (8 * byte_length)) - 1
    int_value = int(np.clip(value, 0, max_int))
    return format(int_value, f"0{byte_length * 2}X")


def _build_positive_response(did: str, value: float, byte_length: int) -> str:
    """Build a UDS positive response hex string: 62 + DID + data."""
    data_hex = _encode_value_hex(value, byte_length)
    return f"{POSITIVE_RESPONSE_SID}{did}{data_hex}"


def generate_uds_sequences(
    n: int = 2500,
    fault_rate: float = 0.0,
    rng_seed: int | None = None,
) -> list[dict[str, Any]]:
    """Generate *n* UDS 0x22 response sequences.

    Parameters
    ----------
    n:
        Number of sequences to generate.
    fault_rate:
        Fraction of sequences that will be marked as faults (0.0–1.0).
        Actual fault injection is handled by ``fault_injector``, but
        this parameter pre-marks sequences so the caller can request
        "clean" data by passing 0.0.
    rng_seed:
        Optional seed for reproducibility.

    Returns
    -------
    list[dict]:
        Each dict contains: signal_id, timestamp, value, signal_type,
        service_id, fault_label.
    """
    rng = np.random.default_rng(rng_seed)
    did_keys = list(DIDS.keys())
    base_time = datetime.now(tz=UTC)

    sequences: list[dict[str, Any]] = []
    for i in range(n):
        did_key = did_keys[i % len(did_keys)]
        did_info = DIDS[did_key]

        # Normal value within operating range + small Gaussian noise
        raw_value = rng.uniform(did_info["min"], did_info["max"])
        noise = rng.normal(0, (did_info["max"] - did_info["min"]) * 0.01)
        value = float(np.clip(raw_value + noise, did_info["min"], did_info["max"]))

        response_hex = _build_positive_response(
            did_key, value, did_info["byte_length"]
        )
        timestamp = base_time + timedelta(milliseconds=i * 10)

        sequences.append(
            {
                "signal_id": str(uuid.uuid4()),
                "timestamp": timestamp.isoformat(),
                "value": response_hex,
                "signal_type": "UDS",
                "service_id": UDS_SERVICE_ID,
                "fault_label": False,
            }
        )

    # Pre-mark faults if requested (values will be overwritten by fault_injector)
    if fault_rate > 0.0:
        n_faults = int(n * fault_rate)
        fault_indices = rng.choice(n, size=n_faults, replace=False)
        for idx in fault_indices:
            sequences[int(idx)]["fault_label"] = True

    return sequences
