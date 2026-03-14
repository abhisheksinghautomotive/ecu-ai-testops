# Phase 2 — Test Runner

> **Goal:** Run structured YAML test cases against the signal log and produce a machine-readable pass/fail report.

---

## What it does

Think of this as a **referee**. You describe expected ECU behaviour in simple YAML test case files:

```yaml
test_id: UDS_0x22_BattVoltage_001
signal_type: UDS
service_id: "0x22"
expected:
  min: 11.0
  max: 15.0
```

The test runner reads these files, finds the matching signal log rows, checks whether the measured values are within tolerance, and writes a structured JSON report.

---

## Key Files

| File | Purpose |
|------|---------|
| `test_runner/test_loader.py` | Reads and validates YAML test case files against the MTF schema |
| `test_runner/signal_matcher.py` | Finds the right signal log row(s) for each test case |
| `test_runner/result_writer.py` | Writes the JSON results file with pass/fail for each test |
| `test_runner/__main__.py` | CLI entry point |
| `test_cases/` | 20 pre-written YAML test cases (10 UDS + 10 OBD) |

---

## Signal Matching Rules

Because the signal log can contain many rows per `service_id`, matching is done carefully:

| Protocol | Matching Strategy |
|----------|------------------|
| **UDS** | Use the **most recent row** where `signal_type = "UDS"` and `service_id` matches |
| **OBD** | Use the **last 100 rows**, take the **median value** to filter out noise |

---

## Running the Test Runner

```bash
python -m test_runner \
  --log ./data/signal_log.parquet \
  --tests ./test_cases/ \
  --output ./data/test_results.json
```

---

## Output Format (`data/test_results.json`)

```json
{
  "summary": {
    "total": 20,
    "passed": 17,
    "failed": 3,
    "pass_rate": 0.85,
    "generated_at": "2025-01-01T00:00:00Z"
  },
  "results": [
    {
      "test_id": "UDS_0x22_BattVoltage_001",
      "status": "passed",
      "actual_value": 12.4,
      "expected_min": 11.0,
      "expected_max": 15.0
    }
  ]
}
```

> **Note:** The `summary` block is intentionally included so the Phase 4 RCA Agent knows which tests to investigate without reading all results.

---

## YAML Schema Validation

All test cases are validated against the MTF (Modular Test Framework) schema before any results are written. Invalid test cases fail fast with a clear error message.

---

## Tests

```bash
pytest tests/test_runner/ --cov=test_runner
```

Coverage minimum: **80%**
