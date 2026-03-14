# Phase 1 — Signal Simulator

> **Goal:** Generate realistic automotive ECU diagnostic data that all subsequent phases consume.

---

## What it does

This phase simulates the two main automotive diagnostic protocols used in real-world ECU testing:

- **UDS (Unified Diagnostic Services)** — Used to query specific ECU memory registers, like reading a sensor calibration value or software version. Responses come back as hex strings.
- **OBD-II (On-Board Diagnostics)** — The standard "check engine" protocol found in every modern car. Gives continuous operating values like RPM, coolant temperature, and throttle position.

Rather than single isolated data points, the simulator outputs **grouped sequences** of 5–20 readings that share the same `signal_id`, mimicking a real diagnostic session where a tool polls the same register repeatedly over time.

---

## Key Files

| File | Purpose |
|------|---------|
| `simulator/uds_simulator.py` | Generates UDS 0x22 diagnostic response sequences |
| `simulator/obd_simulator.py` | Generates OBD-II PID reading sequences |
| `simulator/fault_injector.py` | Corrupts a configurable percentage of sequences to simulate faults |

---

## Types of Faults Injected

| Fault Type | What it simulates |
|------------|------------------|
| **NRC (Negative Response Code)** | ECU refuses the request — returns an error code instead of a value |
| **Timeout** | ECU doesn't respond within the expected time window |
| **Out-of-range** | ECU returns a physically impossible value (e.g., battery voltage of 500V) |

The `fault_injector.py` corrupts **entire sequences** at once (every row sharing a `signal_id`), which ensures the statistical features extracted in Phase 3 clearly reflect the fault.

---

## Output

A Parquet file at `data/signal_log.parquet` with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `signal_id` | string | UUID grouping all rows in one diagnostic sequence |
| `timestamp` | string (ISO8601) | When this reading was taken |
| `value` | string | Raw diagnostic value (numeric string or hex string) |
| `signal_type` | string | `"UDS"` or `"OBD"` |
| `service_id` | string | e.g. `"0x22"` for UDS, `"0x0C"` for OBD RPM |
| `fault_label` | bool | `True` if this row belongs to an injected fault sequence |

This file is the shared input for Phase 2 (Test Runner) and Phase 3 (Anomaly Detector).

---

## Running the Simulator

```bash
python -m simulator --n-uds 2500 --n-obd 2500 --fault-rate 0.1 --output ./data/signal_log.parquet
```

- `--n-uds` / `--n-obd`: Number of sequences to generate per protocol
- `--fault-rate`: Fraction of sequences to corrupt (default `0.1` = 10%)
- `--output`: Where to write the Parquet file

---

## Tests

```bash
pytest tests/simulator/ --cov=simulator
```

Coverage minimum: **80%**
