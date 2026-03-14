"""
Writes execution results to test_results.json including a summary block.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def write_results(results: list[dict[str, Any]], output_path: str | Path) -> str:
    """
    Generate summary block and write full results to a JSON file.

    Args:
        results: List of test result dictionaries from the signal match engine.
        output_path: Destination path for the JSON file.

    Returns:
        Absolute path to the written JSON file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = total - passed
    pass_rate = round(passed / total, 4) if total > 0 else 0.0

    output_data = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "generated_at": datetime.now(UTC).isoformat(),
        },
        "results": results,
    }

    with path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    return str(path.resolve())
