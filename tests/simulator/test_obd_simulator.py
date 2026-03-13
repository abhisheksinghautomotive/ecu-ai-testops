"""Tests for simulator.obd_simulator module."""

from __future__ import annotations

from typing import Any

from simulator.obd_simulator import PIDS, generate_obd_sequences

REQUIRED_FIELDS = {
    "signal_id", "timestamp", "value",
    "signal_type", "service_id", "fault_label",
}


class TestGenerateObdSequences:
    """Tests for generate_obd_sequences."""

    def test_returns_correct_count(self) -> None:
        result = generate_obd_sequences(n=60, rng_seed=1)
        assert len(result) == 60

    def test_required_fields_present(
        self, sample_obd_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_obd_sequences:
            assert REQUIRED_FIELDS.issubset(seq.keys())

    def test_signal_type_is_obd(
        self, sample_obd_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_obd_sequences:
            assert seq["signal_type"] == "OBD"

    def test_service_id_matches_pid(
        self, sample_obd_sequences: list[dict[str, Any]]
    ) -> None:
        valid_service_ids = {f"0x{pid}" for pid in PIDS}
        for seq in sample_obd_sequences:
            assert seq["service_id"] in valid_service_ids

    def test_rpm_value_in_range(self) -> None:
        """Engine RPM (PID 0x0C) should be within 0–8000."""
        sequences = generate_obd_sequences(n=300, fault_rate=0.0, rng_seed=1)
        rpm_seqs = [s for s in sequences if s["service_id"] == "0x0C"]
        for seq in rpm_seqs:
            value = float(seq["value"])
            assert 0.0 <= value <= 8000.0

    def test_coolant_temp_in_range(self) -> None:
        """Coolant temp (PID 0x05) should be within -40–215°C."""
        sequences = generate_obd_sequences(n=300, fault_rate=0.0, rng_seed=1)
        temp_seqs = [s for s in sequences if s["service_id"] == "0x05"]
        for seq in temp_seqs:
            value = float(seq["value"])
            assert -40.0 <= value <= 215.0

    def test_o2_sensor_in_range(self) -> None:
        """O2 sensor (PID 0x14) should be within 0–1.275V."""
        sequences = generate_obd_sequences(n=300, fault_rate=0.0, rng_seed=1)
        o2_seqs = [s for s in sequences if s["service_id"] == "0x14"]
        for seq in o2_seqs:
            value = float(seq["value"])
            assert 0.0 <= value <= 1.275

    def test_no_faults_when_rate_zero(
        self, sample_obd_sequences: list[dict[str, Any]]
    ) -> None:
        for seq in sample_obd_sequences:
            assert seq["fault_label"] is False

    def test_fault_marking_when_rate_positive(self) -> None:
        sequences = generate_obd_sequences(n=100, fault_rate=0.15, rng_seed=1)
        n_faults = sum(1 for s in sequences if s["fault_label"])
        assert n_faults == 15

    def test_signal_ids_are_unique(
        self, sample_obd_sequences: list[dict[str, Any]]
    ) -> None:
        ids = [s["signal_id"] for s in sample_obd_sequences]
        assert len(ids) == len(set(ids))

    def test_zero_sequences(self) -> None:
        result = generate_obd_sequences(n=0, rng_seed=1)
        assert result == []

    def test_reproducibility_with_seed(self) -> None:
        run1 = generate_obd_sequences(n=10, rng_seed=77)
        run2 = generate_obd_sequences(n=10, rng_seed=77)
        for s1, s2 in zip(run1, run2, strict=False):
            assert s1["value"] == s2["value"]
