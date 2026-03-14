"""
CLI entry point for the test runner service.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from test_runner.result_writer import write_results
from test_runner.signal_matcher import run_test_case
from test_runner.test_loader import load_test_cases


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Runner Execution Service")
    parser.add_argument(
        "--log", type=str, required=True, help="Path to the signal log parquet file"
    )
    parser.add_argument(
        "--tests", type=str, required=True, help="Path to the test cases directory"
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to the output results JSON file"
    )

    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"Error: Signal log file not found at {log_path}", file=sys.stderr)
        sys.exit(1)

    try:
        signal_log = pd.read_parquet(log_path)
    except Exception as e:
        print(f"Error reading parquet log: {e}", file=sys.stderr)
        sys.exit(1)

    tests_dir = Path(args.tests)
    if not tests_dir.exists() or not tests_dir.is_dir():
        print(f"Error: Test cases directory not found at {tests_dir}", file=sys.stderr)
        sys.exit(1)

    all_tests = []

    # Load all YAML files in the tests directory
    for yaml_file in tests_dir.glob("*.yaml"):
        try:
            cases = load_test_cases(yaml_file)
            all_tests.extend(cases)
        except Exception as e:
            print(f"Warning: Failed to load {yaml_file}: {e}", file=sys.stderr)

    if not all_tests:
        print("Error: No valid test cases found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(all_tests)} test cases. Executing...")

    results = []
    for case in all_tests:
        res = run_test_case(case, signal_log)
        results.append(res)

    output_path = write_results(results, args.output)
    print(f"Execution complete. Results written to {output_path}")


if __name__ == "__main__":
    main()
