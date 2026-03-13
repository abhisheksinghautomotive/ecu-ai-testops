# ECU AI TestOps Platform

[![CI](https://github.com/abhisheksinghautomotive/ecu-ai-testops/actions/workflows/ci.yml/badge.svg)](https://github.com/abhisheksinghautomotive/ecu-ai-testops/actions/workflows/ci.yml)

**AI-powered ECU test intelligence platform combining automotive HIL/SDV test simulation, ML anomaly detection, and LangChain agentic automation — deployed on Kubernetes via GitHub Actions.**

This is a portfolio project that simulates a real-world automotive CI/CD and AI-assisted testing environment. It combines DevOps pipeline engineering, automotive ECU test simulation, and AI/Agentic automation into a single deployable system.

---

## 🚀 Key Features

- **Automated Root Cause Analysis (RCA)**: LangChain AI agent performs automated root cause analysis on failing test logs.
- **Anomaly Detection**: Scikit-Learn `Isolation Forest` ML model flags abnormal UDS and OBD-II signal patterns.
- **AI Test-Case Generation**: LLM agent with RAG reads ECU spec PDFs to generate industry-standard MTF-format test cases automatically.
- **Automated Quality Gates**: CI/CD pipelines managed via GitHub Actions with GHCR, GitHub Packages, and strict approval gates.
- **Microservices Architecture**: Containerized services orchestrated on Kubernetes (k3s).

---

## 🛠️ Technology Stack

### ⚙️ DevOps & Cloud
- **CI/CD**: GitHub Actions
- **Containers & Orchestration**: Docker, Docker Compose, Kubernetes (k3s)
- **Infrastructure as Code (IaC)**: Terraform
- **Artifacts**: GitHub Container Registry (GHCR), GitHub Packages (PyPI)
- **Object Storage**: MinIO (S3-compatible)
- **Observability**: Prometheus & Grafana

### 🚘 Automotive Simulation
- **Signal Generation**: Simulated UDS 0x22 and OBD-II diagnostic responses.
- **Test Output**: MTF-compatible YAML format test cases.
- **Libraries**: `python-can`, `cantools`

### 🧠 AI & Machine Learning
- **Anomaly Detection**: `scikit-learn` (Isolation Forest), `pandas`, `numpy`
- **Agentic Automation**: `LangChain`, OpenAI `GPT-4o`
- **RAG & Knowledge Base**: `ChromaDB`, `PyMuPDF`

---

## 📁 Repository Structure

```text
ecu-ai-testops/
├── .github/workflows/       # CI/CD Pipelines (pr-check, ci, cd)
├── simulator/               # Phase 1: UDS/OBD-II Signal Generator & Fault Injector
├── tests/                   # Pytest test suite (>80% coverage)
├── docs/                    # Architecture and capability documentation
├── pyproject.toml           # Project configuration (Ruff, MyPy, Pytest)
└── README.md
```

## 🚥 Quality Gates
This project enforces strict development standards before branch merges:
1. **Ruff** for linting.
2. **MyPy** for strict static type checking.
3. **Pytest** for unit tests, enforcing a minimum of **80% coverage**.

## 📄 License
This is a portfolio project. See the repository documentation for further details.
