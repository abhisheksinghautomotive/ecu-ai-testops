# Phase 3 — Anomaly Detector

> **Goal:** Use machine learning to automatically flag ECU signal sequences that deviate from normal behaviour, without hand-written rules.

---

## What it does

Instead of saying "temperature must be < 120°C", the anomaly detector **learns** what normal signal behaviour looks like and flags anything that significantly deviates from it.

It uses **Isolation Forest** — an unsupervised ML algorithm designed for anomaly detection. "Unsupervised" means it doesn't need labelled examples of every possible failure; it learns to isolate unusual patterns on its own.

---

## Why Two Separate Models?

UDS and OBD signals have fundamentally different statistical distributions:

| Protocol | Signal Nature |
|----------|--------------|
| **UDS** | Hex-encoded, narrow value range, low spread |
| **OBD** | Continuous numbers, naturally wider variance |

Mixing them into one model confuses the algorithm. So we train a **UDS model** and an **OBD model** separately, then apply the right one during inference.

---

## Key Files

| File | Purpose |
|------|---------|
| `anomaly_detector/feature_extractor.py` | Converts raw signal rows into numerical ML features per sequence |
| `anomaly_detector/trainer.py` | Trains UDS and OBD Isolation Forest models and serialises them to MinIO |
| `anomaly_detector/detector.py` | Loads trained models and scores new signal data |
| `anomaly_detector/evaluator.py` | Calculates Precision, Recall, F1 against ground truth labels |
| `anomaly_detector/storage_client.py` | Saves/loads models and reports to/from MinIO (S3-compatible storage) |
| `anomaly_detector/__main__.py` | CLI entry point |

---

## Features Extracted Per Sequence

Each `signal_id` group is summarised into these numerical features before being passed to the model:

| Feature | What it captures |
|---------|----------------|
| `mean` | Average value across all readings in the sequence |
| `std` | How much values fluctuate (standard deviation) |
| `min` / `max` | Lowest and highest value seen |
| `value_spread` | `max - min` — a direct measure of range |
| `error_rate` | Fraction of readings that were errors (timeouts, NRCs) |
| `sequence_length` | Total number of readings in the sequence |
| `is_uds` / `is_obd` | Which protocol, encoded as `0.0` or `1.0` |
| `uds_spread` | `is_uds × value_spread` — helps isolate UDS-specific anomalies |

---

## CLI Usage

**Train the model:**
```bash
python -m anomaly_detector --mode train --log ./data/signal_log.parquet
```

**Detect anomalies:**
```bash
python -m anomaly_detector --mode detect \
  --log ./data/signal_log.parquet \
  --output ./data/anomaly_report.json
```

---

## Output Format (`data/anomaly_report.json`)

```json
{
  "metadata": {
    "total_sequences": 500,
    "total_anomalies": 49,
    "anomaly_rate": 0.098,
    "generated_at": "2025-01-01T00:00:00Z"
  },
  "anomalies": [
    {
      "signal_id": "abc-123",
      "anomaly_score": 0.82,
      "features": {
        "min": -999.0,
        "max": -999.0,
        "error_rate": 1.0,
        "value_spread": 0.0,
        "sequence_length": 10.0
      }
    }
  ]
}
```

A higher `anomaly_score` means the sequence is more unusual. Anything predicted as `-1` by the model is flagged.

---

## Performance

Achieved **>0.80 Precision** on synthetic data with 10% fault injection rate. The quality gate is **0.75 Precision** — the phase is not considered complete if this is not met.

---

## Storage

All model artifacts and reports are stored in **MinIO** — never on the local filesystem.

Start MinIO locally:
```bash
docker compose up -d
```

This creates two buckets automatically:
- `model-artifacts` — trained `.pkl` model files
- `reports` — JSON anomaly reports

Required environment variables (put in `.env`, never commit):
```env
S3_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
```

---

## Tests

```bash
pytest tests/test_anomaly_detector_*.py --cov=anomaly_detector
```

Coverage minimum: **80%** (currently at **~94%**)

| Module | Coverage |
|--------|---------|
| `feature_extractor.py` | 90% |
| `trainer.py` | 100% |
| `detector.py` | 98% |
| `evaluator.py` | 90% |
| `storage_client.py` | 91% |
