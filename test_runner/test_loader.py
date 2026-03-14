"""
Test case loader and schema validator.
"""

from pathlib import Path
from typing import Any

import yaml


class InvalidTestCaseError(Exception):
    """Exception raised for invalid test case schema or YAML parsing errors."""

    pass


def load_test_cases(file_path: str | Path) -> list[dict[str, Any]]:
    """
    Load and validate test cases from a YAML file.

    Args:
        file_path: Path to the YAML file.

    Returns:
        List of validated test case dictionaries.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Test case file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidTestCaseError(f"Invalid YAML format in {path}: {e}") from e

    if not isinstance(data, list):
        raise InvalidTestCaseError(f"Test cases must be a list of objects in {path}")

    valid_cases = []
    for i, case in enumerate(data):
        try:
            valid_case = _validate_test_case(case)
            valid_cases.append(valid_case)
        except ValueError as e:
            raise InvalidTestCaseError(
                f"Validation error in {path} at index {i}: {e}"
            ) from e

    return valid_cases


def _validate_test_case(case: Any) -> dict[str, Any]:
    """
    Validate a single test case object against the schema.
    """
    if not isinstance(case, dict):
        raise ValueError("Test case must be a dictionary")

    required_fields = [
        "test_id",
        "signal_type",
        "service_id",
        "expected_response",
        "max_response_time_ms",
    ]
    for field in required_fields:
        if field not in case:
            raise ValueError(f"Missing required field: '{field}'")

    if case["signal_type"] not in ["UDS", "OBD"]:
        raise ValueError(
            f"Invalid signal_type: '{case['signal_type']}'. Must be UDS or OBD."
        )

    if case["signal_type"] == "OBD" and "tolerance" not in case:
        raise ValueError("Missing 'tolerance' field for OBD test case.")

    # Type checking
    if not isinstance(case["test_id"], str):
        raise ValueError("'test_id' must be a string")
    if not isinstance(case["service_id"], str):
        raise ValueError("'service_id' must be a string")
    if not isinstance(case["max_response_time_ms"], (int, float)):
        raise ValueError("'max_response_time_ms' must be a number")

    if case["signal_type"] == "OBD":
        if not isinstance(case["expected_response"], (int, float)):
            raise ValueError("'expected_response' must be a number for OBD")
        if not isinstance(case["tolerance"], (int, float)):
            raise ValueError("'tolerance' must be a number for OBD")
    else:
        if not isinstance(case["expected_response"], str):
            raise ValueError("'expected_response' must be a string for UDS")

    return dict(case)
