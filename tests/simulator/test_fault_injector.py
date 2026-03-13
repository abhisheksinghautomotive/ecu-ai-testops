"""Tests for simulator.fault_injector module."""

from __future__ import annotations

from typing import Any

from simulator.fault_injector import (
    FAULT_TYPES,
    NEGATIVE_RESPONSE_SID,
    TIMEOUT_SENTINEL,
    inject_faults,
)


class TestInjectFaults:
    """Tests for inject_faults."""

    def test_zero_rate_produces_no_faults(
        self, sample_mixed_sequences: list[dict[str, Any]]
    ) -> None:
        result = inject_faults(sample_mixed_sequences, fault_rate=0.0, rng_seed=1)
        for seq in result:
            assert seq["fault_label"] is False

    def test_full_rate_produces_all_faults(
        self, sample_mixed_sequences: list[dict[str, Any]]
    ) -> None:
        result = inject_faults(sample_mixed_sequences, fault_rate=1.0, rng_seed=1)
        for seq in result:
            assert seq["fault_label"] is True

    def test_ten_percent_rate(
        self, sample_mixed_sequences: list[dict[str, Any]]
    ) -> None:
        result = inject_faults(sample_mixed_sequences, fault_rate=0.1, rng_seed=1)
        n_faults = sum(1 for s in result if s["fault_label"])
        expected = int(len(sample_mixed_sequences) * 0.1)
        assert n_faults == expected

    def test_does_not_mutate_original(
        self, sample_mixed_sequences: list[dict[str, Any]]
    ) -> None:
        original_values = [s["value"] for s in sample_mixed_sequences]
        inject_faults(sample_mixed_sequences, fault_rate=0.5, rng_seed=1)
        for orig, seq in zip(original_values, sample_mixed_sequences, strict=False):
            assert seq["value"] == orig

    def test_nrc_error_format(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        """At 100% rate, verify NRC errors contain the negative response SID."""
        result = inject_faults(sample_uds_sequences, fault_rate=1.0, rng_seed=10)
        nrc_seqs = [s for s in result if s["value"].startswith(NEGATIVE_RESPONSE_SID)]
        # With 3 fault types, roughly 1/3 should be NRC (deterministic with seed)
        assert len(nrc_seqs) > 0

    def test_timeout_sentinel_present(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        result = inject_faults(sample_uds_sequences, fault_rate=1.0, rng_seed=10)
        timeout_seqs = [s for s in result if s["value"] == TIMEOUT_SENTINEL]
        assert len(timeout_seqs) > 0

    def test_out_of_range_present(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        result = inject_faults(sample_uds_sequences, fault_rate=1.0, rng_seed=10)
        oor_seqs = [s for s in result if s["value"] in ("FFFF", "0000")]
        assert len(oor_seqs) > 0

    def test_empty_input(self) -> None:
        result = inject_faults([], fault_rate=0.5, rng_seed=1)
        assert result == []

    def test_fault_types_constant(self) -> None:
        assert len(FAULT_TYPES) == 3

    def test_preserves_sequence_length(
        self, sample_mixed_sequences: list[dict[str, Any]]
    ) -> None:
        result = inject_faults(sample_mixed_sequences, fault_rate=0.3, rng_seed=1)
        assert len(result) == len(sample_mixed_sequences)

    def test_reproducibility_with_seed(
        self, sample_uds_sequences: list[dict[str, Any]]
    ) -> None:
        run1 = inject_faults(sample_uds_sequences, fault_rate=0.2, rng_seed=42)
        run2 = inject_faults(sample_uds_sequences, fault_rate=0.2, rng_seed=42)
        for s1, s2 in zip(run1, run2, strict=False):
            assert s1["value"] == s2["value"]
            assert s1["fault_label"] == s2["fault_label"]
