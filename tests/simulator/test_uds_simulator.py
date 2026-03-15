"""Tests for simulator.uds_simulator module."""

from __future__ import annotations

from typing import Any

from simulator.uds_simulator import (
    DIDS,
    POSITIVE_RESPONSE_SID,
    UDS_SERVICE_ID,
    generate_uds_sequences,
)

REQUIRED_FIELDS = {
    "signal_id", "timestamp", "value",
    "signal_type", "service_id", "fault_label",
}


class TestGenerateUdsSequences:
    """Tests for generate_uds_sequences."""

    def test_returns_correct_count(self) -> None:
        # n=10 sequences of 5–20 rows each: total rows >= 10
        result = generate_uds_sequences(n=10, rng_seed=1)
        assert len(result) >= 10

    def test_required_fields_present(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_uds_sequences:
            assert REQUIRED_FIELDS.issubset(seq.keys())

    def test_signal_type_is_uds(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_uds_sequences:
            assert seq["signal_type"] == "UDS"

    def test_service_id_is_0x22(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_uds_sequences:
            assert seq["service_id"] == UDS_SERVICE_ID

    def test_value_starts_with_positive_response(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_uds_sequences:
            assert seq["value"].startswith(POSITIVE_RESPONSE_SID)

    def test_value_contains_valid_did(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        valid_dids = set(DIDS.keys())
        for seq in sample_uds_sequences:
            # Value format: 62 + DID(4 hex chars) + data
            did_in_value = seq["value"][2:6]
            assert did_in_value in valid_dids

    def test_no_faults_when_rate_zero(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_uds_sequences:
            assert seq["fault_label"] is False

    def test_fault_marking_when_rate_positive(self) -> None:
        # With n=20 sequences and fault_rate=0.2, at least 1 sequence is faulted
        sequences = generate_uds_sequences(n=20, fault_rate=0.2, rng_seed=1)
        n_faults = sum(1 for s in sequences if s["fault_label"])
        assert n_faults > 0

    def test_signal_ids_grouped(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        # Multiple rows share the same signal_id (sequence grouping)
        ids = [s["signal_id"] for s in sample_uds_sequences]
        unique_ids = set(ids)
        # Should have fewer unique IDs than total rows
        assert len(unique_ids) < len(ids)

    def test_timestamps_are_ordered(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        timestamps = [s["timestamp"] for s in sample_uds_sequences]
        assert timestamps == sorted(timestamps)

    def test_zero_sequences(self) -> None:
        result = generate_uds_sequences(n=0, rng_seed=1)
        assert result == []

    def test_reproducibility_with_seed(self) -> None:
        run1 = generate_uds_sequences(n=5, rng_seed=99)
        run2 = generate_uds_sequences(n=5, rng_seed=99)
        for s1, s2 in zip(run1, run2, strict=False):
            assert s1["value"] == s2["value"]
