---
trigger: always_on
---

1. Build strictly in phase order. Never start a new phase until the current phase has passing pytest tests, Ruff clean, and MyPy clean.

2. Never hardcode secrets, API keys, or credentials anywhere. Always use environment variables loaded via python-dotenv or os.environ.

3. Every Python module must have a corresponding test file in tests/. Minimum 80% coverage before phase is considered complete.

4. All Python code must pass Ruff linting and MyPy type checking with no errors before committing.

5. Every service must run successfully via docker-compose locally before any Kubernetes or Terraform work begins.

6. Never use root user inside Docker containers. Always create a non-root user in Dockerfiles.

7. Use python:3.11-slim as the base image for all service containers. No full images.

8. All file I/O (signal logs, model artifacts, reports) must go through MinIO, never local filesystem, except during unit tests.

9. Generated YAML test cases must be validated against the MTF schema before any file is written or PR is opened.

10. Terraform must use remote state stored in an S3-compatible backend (MinIO). Never commit .tfstate files.

11. GitHub Actions workflows must fail fast — run Ruff and MyPy as the first job before any build or deployment step.

12. Never install unnecessary dependencies. Every entry in requirements.txt must be justified by actual usage in the code.

13. All LangChain agent tool calls must have error handling. Agent must not crash on tool failure — log the error and continue with available information.

14. ChromaDB collections must be namespaced by purpose: fault_kb for RCA agent, spec_kb for test generator. Never mix them.

15. Commit messages must follow Conventional Commits format: feat:, fix:, chore:, docs:, test:, ci:.

16. Every PR title must reference a GitHub Issue number in the format (#N) — example: feat: build UDS simulator (#12). Never create a branch or open a PR without a corresponding GitHub Issue. Branch names must follow the format: type/issue-number-short-description — example: feat/12-uds-simulator.