"""
Assertion engine for matching test cases against the signal log.
"""

from typing import Any

import pandas as pd


class SignalMatchError(Exception):
    """Exception raised when signal matching fails due to missing data."""

    pass


def run_test_case(
    test_case: dict[str, Any], signal_log: pd.DataFrame, obd_window_size: int = 100
) -> dict[str, Any]:
    """
    Run a single test case against the signal log.

    Args:
        test_case: Validated test case dictionary.
        signal_log: DataFrame containing signal data.
        obd_window_size: Number of recent rows to consider for OBD median calculation.

    Returns:
        Dictionary containing the test result.
    """
    test_id = test_case["test_id"]
    signal_type = test_case["signal_type"]
    service_id = test_case["service_id"]
    expected_response = test_case["expected_response"]

    # Filter by signal_type and service_id
    filtered_log = signal_log[
        (signal_log["signal_type"] == signal_type)
        & (signal_log["service_id"] == service_id)
    ]

    if filtered_log.empty:
        return _create_result(
            test_id,
            "FAIL",
            None,
            expected_response,
            error_msg=(
                f"No signals found for type {signal_type} and service {service_id}"
            ),
        )

    # Sort by timestamp to ensure chronological order
    filtered_log = filtered_log.sort_values(by="timestamp", ascending=True)

    if signal_type == "UDS":
        return _match_uds(test_id, expected_response, filtered_log)
    elif signal_type == "OBD":
        tolerance = test_case["tolerance"]
        return _match_obd(
            test_id, expected_response, tolerance, filtered_log, obd_window_size
        )
    else:
        return _create_result(
            test_id,
            "FAIL",
            None,
            expected_response,
            error_msg=f"Unknown signal_type: {signal_type}",
        )


def _match_uds(test_id: str, expected: str, log: pd.DataFrame) -> dict[str, Any]:
    """Match UDS signals (exact match or startswith on most recent row)."""
    latest_row = log.iloc[-1]
    actual_value = str(latest_row["value"])

    if actual_value.startswith(expected) or actual_value == expected:
        if latest_row.get("fault_label", False):
            return _create_result(
                test_id,
                "FAIL",
                actual_value,
                expected,
                error_msg=(
                    "Match successful, but fault_label is True indicating anomaly"
                ),
            )
        return _create_result(test_id, "PASS", actual_value, expected)
    else:
        return _create_result(
            test_id,
            "FAIL",
            actual_value,
            expected,
            delta=f"Expected {expected}, got {actual_value}",
        )


def _match_obd(
    test_id: str, expected: float, tolerance: float, log: pd.DataFrame, window_size: int
) -> dict[str, Any]:
    """Match OBD signals (median of recent window within tolerance)."""
    window = log.tail(window_size)

    try:
        numeric_values = pd.to_numeric(window["value"], errors="coerce")
        median_value = float(numeric_values.median())
    except Exception as e:
        return _create_result(
            test_id,
            "FAIL",
            None,
            expected,
            error_msg=f"Failed to calculate numeric median: {e}",
        )

    difference = abs(median_value - expected)

    faults_count = (
        window["fault_label"].fillna(False).sum() if "fault_label" in window else 0
    )
    if faults_count > window_size * 0.5:
        return _create_result(
            test_id,
            "FAIL",
            median_value,
            expected,
            error_msg=f"Window contains high fault rate ({faults_count}/{len(window)})",
        )

    if difference <= tolerance:
        return _create_result(test_id, "PASS", median_value, expected)
    else:
        return _create_result(
            test_id,
            "FAIL",
            median_value,
            expected,
            delta=(
                f"Median {median_value:.2f} is outside {expected} "
                f"±{tolerance} (diff: {difference:.2f})"
            ),
        )


def _create_result(
    test_id: str,
    status: str,
    actual: Any,
    expected: Any,
    delta: str | None = None,
    error_msg: str | None = None,
) -> dict[str, Any]:
    """Helper to format a standardized result dictionary."""
    result = {
        "test_id": test_id,
        "status": status,
        "actual_value": actual,
        "expected_value_str": str(expected),
        "execution_time_ms": 0,
    }
    if delta is not None:
        result["delta"] = delta
    if error_msg is not None:
        result["error_msg"] = error_msg

    return result
