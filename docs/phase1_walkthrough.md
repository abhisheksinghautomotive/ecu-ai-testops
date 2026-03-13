# Phase 1 — Signal Simulator: Walkthrough

## What Was Built

| File | Purpose |
|------|---------|
| [pyproject.toml](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/pyproject.toml) | Project config (Ruff, MyPy, pytest, coverage) |
| [uds_simulator.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/uds_simulator.py) | UDS 0x22 ReadDataByIdentifier — 3 DIDs (coolant, RPM, battery) |
| [obd_simulator.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/obd_simulator.py) | OBD-II PIDs (0x0C RPM, 0x05 coolant, 0x14 O2) with Gaussian noise |
| [fault_injector.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/fault_injector.py) | 3 fault types: NRC errors, timeouts, out-of-range values |
| [dataset_writer.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/dataset_writer.py) | Parquet writer with schema validation + auto directory creation |
| [__main__.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/__main__.py) | CLI entry point: defaults 2500+2500 sequences, `--output ./data/signal_log.parquet` |

## Verification Results

### Ruff Linting ✅
```
All checks passed!
```

### MyPy Type Checking ✅
```
Success: no issues found in 6 source files
```

### pytest + Coverage ✅
```
43 passed in 0.39s
Coverage: 80.62% (≥80% threshold)
```

| Module | Stmts | Miss | Cover |
|--------|-------|------|-------|
| [__init__.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/tests/__init__.py) | 1 | 0 | 100% |
| [uds_simulator.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/uds_simulator.py) | 35 | 0 | 100% |
| [obd_simulator.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/obd_simulator.py) | 32 | 0 | 100% |
| [fault_injector.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/fault_injector.py) | 44 | 0 | 100% |
| [dataset_writer.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/dataset_writer.py) | 17 | 0 | 100% |
| [__main__.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/__main__.py) | 31 | 31 | 0% |

> [!NOTE]
> [__main__.py](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/__main__.py) at 0% is expected — it's a CLI wiring module. All business logic modules are at 100%.

### Integration Smoke Test ✅
```
Generating 50 UDS sequences …
Generating 50 OBD-II sequences …
Injecting faults at 10% rate …
Total sequences: 100 | Faults: 10
Wrote signal log to: /private/tmp/test_signal_log.parquet
```

## Parquet Schema
`signal_id | timestamp | value | signal_type | service_id | fault_label`

---

## GitHub Actions Workflows

| File | Purpose |
|------|---------|
| [pr-check.yml](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/.github/workflows/pr-check.yml) | PR title validation: `type: description (#N)` |
| [ci.yml](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/.github/workflows/ci.yml) | `lint` → [test](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/tests/simulator/test_fault_injector.py#71-74) → [build](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/uds_simulator.py#58-62) pipeline |
| [Dockerfile](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/Dockerfile) | `python:3.11-slim`, non-root user |

### CI Pipeline: `lint → test → build`
- **lint**: Ruff + MyPy (blocks all downstream)
- **test**: pytest ≥80% coverage (needs lint)
- **build**: Docker → GHCR (push only on main, build-only on PRs)

### Validation ✅
- Both YAML files pass `yaml.safe_load` syntax check
- Job names `lint`, [test](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/tests/simulator/test_fault_injector.py#71-74), [build](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/uds_simulator.py#58-62) match required status check IDs
- No hardcoded tokens — `secrets.GITHUB_TOKEN` only
- Pip cache keyed on [requirements.txt](file:///Users/abhisheksingh/Documents/projects/ecu-ai-testops/simulator/requirements.txt) hash

---

## GitHub Integration (Phase 1 Commit)
- **Issue:** Created Issue [#1 Build Phase 1 Signal Simulator and CI workflows](https://github.com/abhisheksinghautomotive/ecu-ai-testops/issues/1)
- **Branch:** Developed on feature branch `feat/1-uds-simulator` 
- **Commit:** Followed Conventional Commits `feat: build Signal Simulator and CI workflows (#1)`
- **Pull Request:** Raised PR [#2](https://github.com/abhisheksinghautomotive/ecu-ai-testops/pull/2) for review, linking to Issue #1

## Next Steps
Ready for **Phase 2 — Test Runner**.
