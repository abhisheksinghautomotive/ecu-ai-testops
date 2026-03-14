"""Fault injector for ECU signal sequences.

Injects three types of faults into signal data at a configurable rate:
- NRC (Negative Response Code) errors
- Timeout responses
- Out-of-range values
"""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

# ── NRC codes used in UDS (ISO 14229) ────────────────────────────────
NRC_CODES: dict[str, str] = {
    "22": "conditionsNotCorrect",
    "31": "requestOutOfRange",
    "72": "generalProgrammingFailure",
    "14": "responseTooLong",
    "78": "requestCorrectlyReceivedResponsePending",
}

NEGATIVE_RESPONSE_SID = "7F"
TIMEOUT_SENTINEL = "TIMEOUT"

# Fault type identifiers
FAULT_NRC = "nrc_error"
FAULT_TIMEOUT = "timeout"
FAULT_OUT_OF_RANGE = "out_of_range"
FAULT_TYPES = [FAULT_NRC, FAULT_TIMEOUT, FAULT_OUT_OF_RANGE]


def _inject_nrc_error(sequence: dict[str, Any], rng: np.random.Generator) -> None:
    """Replace value with a UDS negative response code."""
    nrc_key = rng.choice(list(NRC_CODES.keys()))
    # Extract service ID byte from the original service_id field (e.g. "0x22" → "22")
    service_byte = sequence["service_id"].replace("0x", "").upper()
    sequence["value"] = f"{NEGATIVE_RESPONSE_SID}{service_byte}{nrc_key}"
    sequence["fault_label"] = True


def _inject_timeout(sequence: dict[str, Any]) -> None:
    """Replace value with a timeout sentinel."""
    sequence["value"] = TIMEOUT_SENTINEL
    sequence["fault_label"] = True


def _inject_out_of_range(
    sequence: dict[str, Any], rng: np.random.Generator
) -> None:
    """Replace value with an out-of-range extreme value."""
    # Use a very large or very small numeric value encoded as string
    if rng.random() > 0.5:
        # Extremely high value
        sequence["value"] = "FFFF"
    else:
        # Negative / zero anomaly
        sequence["value"] = "0000"
    sequence["fault_label"] = True


def inject_faults(
    sequences: list[dict[str, Any]],
    fault_rate: float = 0.1,
    rng_seed: int | None = None,
) -> list[dict[str, Any]]:
    """Inject faults into a copy of the signal sequences.

    Parameters
    ----------
    sequences:
        List of signal sequence dicts. Each must have at least
        ``value``, ``service_id``, and ``fault_label`` keys.
    fault_rate:
        Fraction of sequences to corrupt (0.0–1.0). Default 10%.
    rng_seed:
        Optional seed for reproducibility.

    Returns
    -------
    list[dict]:
        A new list with faults injected. Original list is not mutated.
    """
    if not sequences:
        return []

    rng = np.random.default_rng(rng_seed)
    result = copy.deepcopy(sequences)

    # Group indices by signal_id so we corrupt entire sequences at once
    signal_groups: dict[str, list[int]] = {}
    for i, seq in enumerate(result):
        sid = seq["signal_id"]
        if sid not in signal_groups:
            signal_groups[sid] = []
        signal_groups[sid].append(i)

    # The total number of sequences is the number of distinct signal_ids
    unique_signals = list(signal_groups.keys())
    n_total_sequences = len(unique_signals)
    n_faults = int(n_total_sequences * fault_rate)

    if n_faults == 0:
        return result

    # Pick signal_ids to corrupt (without replacement)
    fault_signal_indices = rng.choice(n_total_sequences, size=n_faults, replace=False)

    for idx in fault_signal_indices:
        fault_type = rng.choice(FAULT_TYPES)
        faulty_signal_id = unique_signals[int(idx)]
        
        # Apply the chosen fault type to every row in this sequence
        for row_idx in signal_groups[faulty_signal_id]:
            seq = result[row_idx]
            if fault_type == FAULT_NRC:
                _inject_nrc_error(seq, rng)
            elif fault_type == FAULT_TIMEOUT:
                _inject_timeout(seq)
            elif fault_type == FAULT_OUT_OF_RANGE:
                _inject_out_of_range(seq, rng)

    return result
