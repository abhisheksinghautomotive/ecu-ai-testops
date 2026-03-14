# Developer Guide — ECU AI TestOps Platform

> **Start here.** This guide is split by phase. Each page explains what was built, how it works, and how to run it — in plain language.

---

## Phases

| Phase | Document | Status |
|-------|----------|--------|
| 1 | [Signal Simulator](./phase-1-signal-simulator.md) | ✅ Complete |
| 2 | [Test Runner](./phase-2-test-runner.md) | ✅ Complete |
| 3 | [Anomaly Detector](./phase-3-anomaly-detector.md) | ✅ Complete |
| 4 | RCA Agent | 🔜 Planned |
| 5 | AI Test Generator | 🔜 Planned |

---

## Data Flow at a Glance

```
Phase 1: simulator/
  └── Generates signal_log.parquet (UDS + OBD sequences + injected faults)
          │
          ├─► Phase 2: test_runner/
          │       └── Runs YAML test cases → test_results.json
          │
          └─► Phase 3: anomaly_detector/
                  ├── trainer.py  → Trains models → saves to MinIO
                  └── detector.py → Scores signals → anomaly_report.json
                                          │
                                   Phase 4: RCA Agent reads this ▶
```

---

## Quick Start

```bash
# 1. Start local MinIO storage
docker compose up -d

# 2. Generate signal data
python -m simulator --n-uds 2500 --n-obd 2500 --fault-rate 0.1

# 3. Run test cases
python -m test_runner --log ./data/signal_log.parquet --tests ./test_cases/

# 4. Train anomaly model
python -m anomaly_detector --mode train --log ./data/signal_log.parquet

# 5. Detect anomalies
python -m anomaly_detector --mode detect --log ./data/signal_log.parquet
```

---

## Repository Conventions

| Rule | Details |
|------|---------|
| Branch naming | `feat/N-short-description` |
| Commit format | Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `ci:` |
| PR title | Must reference issue number e.g. `feat: build simulator (#1)` |
| Coverage | Minimum **80%** per module before phase is complete |
| Secrets | Always use `.env` + `python-dotenv`, never hardcode credentials |
| Docker | Use `python:3.11-slim`, never run as root inside containers |
| Storage | All artifacts go through MinIO — never local filesystem in production |
