"""
Pytest fixtures for test_runner tests.
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def valid_yaml_file(tmp_path: Path) -> Path:
    cases = [
        {
            "test_id": "UDS_01",
            "signal_type": "UDS",
            "service_id": "0x22",
            "expected_response": "62F1A0",
            "max_response_time_ms": 50,
        },
        {
            "test_id": "OBD_01",
            "signal_type": "OBD",
            "service_id": "0x010C",
            "expected_response": 2000.0,
            "tolerance": 50.0,
            "max_response_time_ms": 100,
        },
    ]
    file_path = tmp_path / "valid_tests.yaml"
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(cases, f)
    return file_path


@pytest.fixture
def invalid_yaml_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "invalid_tests.yaml"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("this: is: invalid: yaml:")
    return file_path


@pytest.fixture
def malformed_cases_yaml_file(tmp_path: Path) -> Path:
    cases = [
        {
            "test_id": "UDS_01",
            "signal_type": "UNKNOWN",  # Invalid type
            "service_id": "0x22",
            "expected_response": "62F1A0",
            "max_response_time_ms": 50,
        }
    ]
    file_path = tmp_path / "malformed_tests.yaml"
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(cases, f)
    return file_path
