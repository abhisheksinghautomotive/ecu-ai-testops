"""
Unit tests for the result_writer module.
"""

import json
from pathlib import Path

from test_runner.result_writer import write_results


def test_write_results(tmp_path: Path) -> None:
    results = [
        {
            "test_id": "UDS_01",
            "status": "PASS",
            "actual_value": "62F1A0",
            "expected_value_str": "62F1A0",
            "execution_time_ms": 10,
        },
        {
            "test_id": "UDS_02",
            "status": "FAIL",
            "actual_value": "7F2213",
            "expected_value_str": "62F1A0",
            "delta": "Expected 62F1A0, got 7F2213",
            "execution_time_ms": 11,
        },
        {
            "test_id": "OBD_01",
            "status": "PASS",
            "actual_value": 2010.0,
            "expected_value_str": "2000.0",
            "execution_time_ms": 15,
        },
    ]

    output_file = tmp_path / "test_results.json"
    written_path = write_results(results, output_file)

    assert Path(written_path).exists()

    with open(written_path, encoding="utf-8") as f:
        data = json.load(f)

    assert "summary" in data
    assert "results" in data

    summary = data["summary"]
    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1
    assert summary["pass_rate"] == 0.6667
    assert "generated_at" in summary

    assert len(data["results"]) == 3
    assert data["results"][0]["test_id"] == "UDS_01"


def test_write_results_empty(tmp_path: Path) -> None:
    output_file = tmp_path / "empty_results.json"
    write_results([], output_file)

    with open(output_file, encoding="utf-8") as f:
        data = json.load(f)

    assert data["summary"]["total"] == 0
    assert data["summary"]["pass_rate"] == 0.0
