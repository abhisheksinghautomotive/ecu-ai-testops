"""Tests for simulator.dataset_writer module."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from simulator.dataset_writer import PARQUET_SCHEMA_COLUMNS, write_parquet


class TestWriteParquet:
    """Tests for write_parquet."""

    def test_creates_parquet_file(
        self,
        sample_mixed_sequences: list[dict[str, Any]],
        tmp_output_path: str,
    ) -> None:
        result_path = write_parquet(sample_mixed_sequences, tmp_output_path)
        assert Path(result_path).exists()

    def test_parquet_schema_matches(
        self,
        sample_mixed_sequences: list[dict[str, Any]],
        tmp_output_path: str,
    ) -> None:
        write_parquet(sample_mixed_sequences, tmp_output_path)
        df = pd.read_parquet(tmp_output_path)
        assert list(df.columns) == PARQUET_SCHEMA_COLUMNS

    def test_data_roundtrip(
        self,
        sample_mixed_sequences: list[dict[str, Any]],
        tmp_output_path: str,
    ) -> None:
        write_parquet(sample_mixed_sequences, tmp_output_path)
        df = pd.read_parquet(tmp_output_path)
        assert len(df) == len(sample_mixed_sequences)
        # Spot-check first record
        first = sample_mixed_sequences[0]
        row = df.iloc[0]
        assert row["signal_id"] == first["signal_id"]
        assert row["signal_type"] == first["signal_type"]

    def test_fault_labels_preserved(
        self,
        sample_uds_sequences: list[dict[str, Any]],
        tmp_output_path: str,
    ) -> None:
        write_parquet(sample_uds_sequences, tmp_output_path)
        df = pd.read_parquet(tmp_output_path)
        expected_faults = sum(1 for s in sample_uds_sequences if s["fault_label"])
        actual_faults = int(df["fault_label"].sum())
        assert actual_faults == expected_faults

    def test_empty_sequences_raises(self, tmp_output_path: str) -> None:
        with pytest.raises(ValueError, match="empty"):
            write_parquet([], tmp_output_path)

    def test_missing_columns_raises(self, tmp_output_path: str) -> None:
        incomplete = [{"signal_id": "abc", "timestamp": "2025-01-01"}]
        with pytest.raises(ValueError, match="Missing"):
            write_parquet(incomplete, tmp_output_path)

    def test_creates_parent_directories(
        self,
        sample_uds_sequences: list[dict[str, Any]],
        tmp_path: Any,
    ) -> None:
        nested = str(tmp_path / "deep" / "nested" / "out.parquet")
        result_path = write_parquet(sample_uds_sequences, nested)
        assert Path(result_path).exists()

    def test_returns_absolute_path(
        self,
        sample_uds_sequences: list[dict[str, Any]],
        tmp_output_path: str,
    ) -> None:
        result_path = write_parquet(sample_uds_sequences, tmp_output_path)
        assert Path(result_path).is_absolute()
