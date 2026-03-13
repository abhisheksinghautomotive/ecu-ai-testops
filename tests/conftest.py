"""Shared pytest fixtures for simulator tests."""

from __future__ import annotations

from typing import Any

import pytest

from simulator.obd_simulator import generate_obd_sequences
from simulator.uds_simulator import generate_uds_sequences


@pytest.fixture
def sample_uds_sequences() -> list[dict[str, Any]]:
    """100 UDS sequences with no faults, reproducible seed."""
    return generate_uds_sequences(n=100, fault_rate=0.0, rng_seed=42)


@pytest.fixture
def sample_obd_sequences() -> list[dict[str, Any]]:
    """100 OBD sequences with no faults, reproducible seed."""
    return generate_obd_sequences(n=100, fault_rate=0.0, rng_seed=42)


@pytest.fixture
def sample_mixed_sequences(
    sample_uds_sequences: list[dict[str, Any]],
    sample_obd_sequences: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Combined UDS + OBD sequences (200 total, no faults)."""
    return sample_uds_sequences + sample_obd_sequences


@pytest.fixture
def tmp_output_path(tmp_path: Any) -> str:
    """Temp file path for Parquet output."""
    return str(tmp_path / "test_signal_log.parquet")
