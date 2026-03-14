"""
Unit tests for the signal_matcher module.
"""

import pandas as pd
import pytest

from test_runner.signal_matcher import run_test_case


@pytest.fixture
def sample_signal_log() -> pd.DataFrame:
    data = [
        {
            "timestamp": 1000,
            "signal_type": "UDS",
            "service_id": "0x22",
            "value": "62F1A0",
            "fault_label": False,
        },
        {
            "timestamp": 1010,
            "signal_type": "UDS",
            "service_id": "0x22",
            "value": "7F2213",
            "fault_label": True,
        },
        {
            "timestamp": 1020,
            "signal_type": "UDS",
            "service_id": "0x22",
            "value": "62F1A0",
            "fault_label": False,
        },
        {
            "timestamp": 1000,
            "signal_type": "OBD",
            "service_id": "0x010C",
            "value": 1950.0,
            "fault_label": False,
        },
        {
            "timestamp": 1010,
            "signal_type": "OBD",
            "service_id": "0x010C",
            "value": 2010.0,
            "fault_label": False,
        },
        {
            "timestamp": 1020,
            "signal_type": "OBD",
            "service_id": "0x010C",
            "value": 2050.0,
            "fault_label": False,
        },
    ]
    return pd.DataFrame(data)


def test_run_test_case_uds_pass(sample_signal_log: pd.DataFrame) -> None:
    case = {
        "test_id": "UDS_01",
        "signal_type": "UDS",
        "service_id": "0x22",
        "expected_response": "62F1A0",
        "max_response_time_ms": 50,
    }
    result = run_test_case(case, sample_signal_log)
    assert result["status"] == "PASS"
    assert result["actual_value"] == "62F1A0"


def test_run_test_case_uds_fail(sample_signal_log: pd.DataFrame) -> None:
    df = sample_signal_log.copy()
    df.loc[2, "value"] = "62FFFF"  # Most recent is idx 2

    case = {
        "test_id": "UDS_01",
        "signal_type": "UDS",
        "service_id": "0x22",
        "expected_response": "62F1A0",
        "max_response_time_ms": 50,
    }
    result = run_test_case(case, df)
    assert result["status"] == "FAIL"
    assert "Expected 62F1A0" in result.get("delta", "")


def test_run_test_case_uds_fault_label(sample_signal_log: pd.DataFrame) -> None:
    df = sample_signal_log.copy()
    df.loc[2, "fault_label"] = True

    case = {
        "test_id": "UDS_01",
        "signal_type": "UDS",
        "service_id": "0x22",
        "expected_response": "62F1A0",
        "max_response_time_ms": 50,
    }
    result = run_test_case(case, df)
    assert result["status"] == "FAIL"
    assert "fault_label is True" in result.get("error_msg", "")


def test_run_test_case_obd_pass(sample_signal_log: pd.DataFrame) -> None:
    case = {
        "test_id": "OBD_01",
        "signal_type": "OBD",
        "service_id": "0x010C",
        "expected_response": 2000.0,
        "tolerance": 50.0,
        "max_response_time_ms": 100,
    }
    result = run_test_case(case, sample_signal_log)
    assert result["status"] == "PASS"
    assert result["actual_value"] == 2010.0


def test_run_test_case_obd_fail_out_of_tolerance(
    sample_signal_log: pd.DataFrame,
) -> None:
    case = {
        "test_id": "OBD_01",
        "signal_type": "OBD",
        "service_id": "0x010C",
        "expected_response": 3000.0,
        "tolerance": 10.0,
        "max_response_time_ms": 100,
    }
    result = run_test_case(case, sample_signal_log)
    assert result["status"] == "FAIL"
    assert "Median 2010.00 is outside 3000.0" in result.get("delta", "")


def test_run_test_case_no_data(sample_signal_log: pd.DataFrame) -> None:
    case = {
        "test_id": "MISSING",
        "signal_type": "OBD",
        "service_id": "0x9999",
        "expected_response": 0.0,
        "tolerance": 1.0,
        "max_response_time_ms": 100,
    }
    result = run_test_case(case, sample_signal_log)
    assert result["status"] == "FAIL"
    assert "No signals found" in result.get("error_msg", "")
