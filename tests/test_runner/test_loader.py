"""
Unit tests for test_loader module.
"""

from pathlib import Path

import pytest

from test_runner.test_loader import (
    InvalidTestCaseError,
    _validate_test_case,
    load_test_cases,
)


def test_load_valid_test_cases(valid_yaml_file: Path) -> None:
    cases = load_test_cases(valid_yaml_file)
    assert len(cases) == 2
    assert cases[0]["test_id"] == "UDS_01"
    assert cases[1]["test_id"] == "OBD_01"


def test_load_nonexistent_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_test_cases("nonexistent_file.yaml")


def test_load_invalid_yaml(invalid_yaml_file: Path) -> None:
    with pytest.raises(InvalidTestCaseError, match="Invalid YAML format"):
        load_test_cases(invalid_yaml_file)


def test_load_malformed_cases(malformed_cases_yaml_file: Path) -> None:
    with pytest.raises(InvalidTestCaseError, match="Validation error"):
        load_test_cases(malformed_cases_yaml_file)


def test_validate_test_case_missing_field() -> None:
    case = {
        "test_id": "UDS_01",
        "signal_type": "UDS",
        # Missing service_id, expected_response, max_response_time_ms
    }
    with pytest.raises(ValueError, match="Missing required field"):
        _validate_test_case(case)


def test_validate_test_case_obd_missing_tolerance() -> None:
    case = {
        "test_id": "OBD_01",
        "signal_type": "OBD",
        "service_id": "0x010C",
        "expected_response": 2000.0,
        "max_response_time_ms": 100,
        # Missing tolerance
    }
    with pytest.raises(ValueError, match="Missing 'tolerance' field"):
        _validate_test_case(case)


def test_validate_test_case_invalid_types() -> None:
    case1 = {
        "test_id": 123,  # Should be string
        "signal_type": "UDS",
        "service_id": "0x22",
        "expected_response": "62F1A0",
        "max_response_time_ms": 50,
    }
    with pytest.raises(ValueError, match="'test_id' must be a string"):
        _validate_test_case(case1)

    case2 = {
        "test_id": "OBD_01",
        "signal_type": "OBD",
        "service_id": "0x010C",
        "expected_response": "2000.0",  # Should be number
        "tolerance": 50.0,
        "max_response_time_ms": 100,
    }
    with pytest.raises(ValueError, match="'expected_response' must be a number"):
        _validate_test_case(case2)
