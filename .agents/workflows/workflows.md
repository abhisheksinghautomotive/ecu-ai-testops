---
description: 
---

/simulate
Generate a fresh batch of synthetic ECU signal data. Run uds_simulator.py and obd_simulator.py with fault injection at 10% rate. Write output to signal_log.parquet. Confirm row count, fault_label distribution, and parquet schema before finishing.

/test
Execute all YAML test cases in test_runner/test_cases/ against the latest signal_log.parquet. Output test_results.json. Print a summary: total tests, passed, failed, skipped. Halt and show failing test details if failure rate exceeds 20%.

/detect
Load the trained Isolation Forest model from MinIO. Score the latest signal_log.parquet. Output anomaly_report.json. Print precision and recall against fault_label ground truth. Warn if precision drops below 0.75.

/analyze
Run the LangChain RCA agent against the latest test_results.json and anomaly_report.json. Generate one RCA report per failing test case. Store all reports in MinIO under rca/latest/. Post a summary to GITHUB_STEP_SUMMARY.

/generate-tests [pdf_path]
Ingest the ECU spec PDF at pdf_path. Embed into ChromaDB spec_kb collection. Generate new MTF-compatible YAML test cases. Validate against schema. Open a draft GitHub PR with the generated test cases on a new branch named feat/generated-tests-{timestamp}.

/train
Retrain the Isolation Forest model on the latest signal_log.parquet using only fault_label=False sequences. Evaluate on full dataset. Print precision, recall, and contamination parameter used. Save new model to MinIO under models/isolation_forest_latest.pkl. Do not overwrite previous model — save with timestamp as well.

/pipeline
Run the full end-to-end pipeline in sequence: /simulate → /test → /detect → /analyze. Halt at any step if it fails. Print a final summary of the entire run: signal count, test results, anomaly count, RCA reports generated.

/build
Build Docker images for all five services. Tag with current git SHA and :dev. Push to GHCR. Print image digests after push. Fail if any service image fails to build.

/deploy
Apply Kubernetes manifests in k8s/ to the k3s cluster. Verify all Deployments reach Ready state within 2 minutes. Print pod status for all namespaces after deploy. Rollback and alert if any Deployment fails.

/infra-plan
Run terraform plan for all modules in terraform/. Print the plan summary. Do not apply. Highlight any destructive changes in the output.

/infra-apply
Run terraform apply for all modules in terraform/. Require explicit confirmation before applying. Print outputs after apply completes.

/lint
Run Ruff and MyPy across the entire codebase. Print all errors grouped by file. Do not autofix — only report. Exit with error if any issues found.

/test-coverage
Run pytest across all services with coverage reporting. Print per-module coverage percentages. Fail and list uncovered modules if any module falls below 80% coverage.

/promote
Promote all service Docker images from :dev tag to :prod tag in GHCR. Require explicit confirmation before tagging. Log all promoted image digests with timestamp.

/status
Print a health summary of the entire platform: k3s pod status, MinIO bucket contents (log count, model count, report count), latest pipeline run result, and ChromaDB collection sizes for fault_kb and spec_kb.

/new-issue [title]
Create a new GitHub Issue with the given title. Apply the appropriate label (feat, fix, chore, docs, test, ci) based on the title context. Output the issue number and the correct branch name to use — format: type/issue-number-short-description. Do not write any code until this workflow completes.