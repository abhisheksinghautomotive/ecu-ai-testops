**ECU TEST INTELLIGENCE PLATFORM**

Project Design Document

*Automotive HIL + SDV \| DevOps \| AI/Agentic*

Version 1.0 \| 2025 \| 100% Free Infrastructure

**1. Project Overview**

The ECU Test Intelligence Platform is a portfolio project that simulates
a real-world automotive CI/CD and AI-assisted testing environment. It
combines three disciplines --- DevOps pipeline engineering, automotive
ECU test simulation, and AI/Agentic automation --- into a single
deployable system.

The platform ingests simulated ECU diagnostic signals (UDS/OBD-II), runs
them through an automated test pipeline, detects anomalies using an ML
model, and invokes an AI agent to perform root cause analysis and
generate new test cases. Everything is containerized, orchestrated on
Kubernetes, and triggered via GitHub Actions.

100% free infrastructure: GitHub Actions, GHCR, GitHub Packages, k3s on
Oracle Cloud free tier, and open-source ML/AI libraries.

**1.1 Problem Statement**

In automotive HIL and SDV validation environments (such as the GM SDV2
project at KPIT), the following pain points exist:

-   Test failures are diagnosed manually by engineers reviewing raw logs
    --- slow and inconsistent

-   Anomalous ECU signal patterns go undetected until late in the test
    cycle

-   Writing new test cases from spec documents is a time-consuming
    manual process

-   No automated promotion or quality gate exists between test
    environments

**1.2 Solution Summary**

The platform automates these four concerns end-to-end:

  -----------------------------------------------------------------------
  **Concern**                  **Solution Component**
  ---------------------------- ------------------------------------------
  Manual log diagnosis         LangChain AI agent performs automated RCA
                               on failing test logs

  Undetected signal anomalies  Isolation Forest ML model flags abnormal
                               UDS/CAN signal patterns

  Manual test case writing     LLM agent reads ECU spec PDFs and
                               generates MTF-format test cases

  No artifact promotion gates  GitHub Actions pipeline with GHCR + GitHub
                               Packages + approval gates
  -----------------------------------------------------------------------

**2. Technology Stack**

  ---------------------------------------------------------------------------
  **Category**    **Technology**   **Purpose**               **Resume
                                                             Keyword**
  --------------- ---------------- ------------------------- ----------------
  DevOps          GitHub Actions   CI/CD pipelines, approval GitHub Actions
                                   gates, scheduled runs     

  DevOps          GitHub Container Store Docker images for   GHCR / Container
                  Registry         all platform services     Registry

  DevOps          GitHub Packages  Publish and consume       GitHub Packages
                  (PyPI)           internal Python packages  

  DevOps          Docker + Docker  Containerize every        Docker
                  Compose          service; local dev        
                                   environment               

  DevOps          Kubernetes (k3s) Orchestrate services on   Kubernetes
                                   Oracle Cloud free VM      

  DevOps          Terraform        Provision Oracle VM, k3s, Terraform / IaC
                                   namespaces, secrets       

  Automotive      Python-can +     Simulate CAN bus signal   CAN Bus /
                  cantools         generation and parsing    Automotive

  Automotive      UDS/OBD-II       Generate realistic ECU    UDS / OBD-II /
                  simulation       diagnostic response       Diagnostics
                                   sequences                 

  Automotive      MTF-format test  AI-generated test cases   TE MTF
                  output           in MTF-compatible YAML    
                                   format                    

  AI / ML         scikit-learn     Anomaly detection on ECU  ML / Anomaly
                  (Isolation       signal time-series data   Detection
                  Forest)                                    

  AI / ML         LangChain        Agentic RCA pipeline      LangChain /
                                   orchestration             Agentic AI

  AI / ML         OpenAI API       LLM for RCA generation    LLM / OpenAI
                  (GPT-4o)         and test case synthesis   

  AI / ML         ChromaDB         Vector store of known ECU Vector DB / RAG
                                   fault patterns for RAG    

  AI / ML         PyMuPDF          Parse ECU spec PDFs for   PDF parsing
                                   test case generation      

  Observability   Prometheus +     Monitor pipeline runs,    Prometheus /
                  Grafana          anomaly rates, agent      Grafana
                                   latency                   

  Storage         MinIO            Store test logs, ML model S3-compatible
                  (self-hosted S3) artifacts, RCA reports    storage
  ---------------------------------------------------------------------------

**3. System Architecture**

**3.1 High-Level Component Map**

The platform has five major components that form a linear pipeline with
feedback loops:

  -----------------------------------------------------------------------------
  **Component**   **Role**                             **Tech**
  --------------- ------------------------------------ ------------------------
  1\. Signal      Generates synthetic CAN/UDS ECU      Python, python-can,
  Simulator       diagnostic signals with injected     cantools
                  faults                               

  2\. Test Runner Executes test cases against          Python, pytest,
                  simulated signals; produces          MTF-format YAML
                  pass/fail + signal logs              

  3\. Anomaly     Reads signal logs; flags abnormal    scikit-learn, pandas,
  Detector        patterns using trained Isolation     numpy
                  Forest                               

  4\. AI Agent    Reads failed test logs + anomaly     LangChain, OpenAI,
  (RCA)           flags; queries ChromaDB; generates   ChromaDB
                  RCA report                           

  5\. Test Case   Reads ECU spec PDF; generates new    LangChain, OpenAI,
  Generator       MTF-format test cases via LLM        PyMuPDF
  -----------------------------------------------------------------------------

**3.2 Pipeline Flow**

  ------------------------------------------------------------------------------
  **Step**   **Trigger**      **Action**                   **Output**
  ---------- ---------------- ---------------------------- ---------------------
  1          Push to main /   GitHub Actions triggers full Pipeline run started
             scheduled cron   pipeline                     

  2          Pipeline step 1  Signal Simulator generates   signal_log.parquet
                              1000 ECU signal sequences    
                              with 10% injected faults     

  3          Pipeline step 2  Test Runner executes all     test_results.json
                              test cases against signal    (pass/fail per case)
                              log                          

  4          Pipeline step 3  Anomaly Detector loads       anomaly_report.json
                              signal log, scores each      
                              sequence, flags outliers     

  5          Pipeline step 4  AI Agent reads failed        rca_report.md (per
                              tests + anomaly report,      failure)
                              queries ChromaDB fault KB,   
                              calls OpenAI                 

  6          Pipeline step 5  RCA report posted as GitHub  Visible in GitHub UI
                              Actions job summary and      
                              stored in MinIO              

  7          On-demand        Test Case Generator reads    new_test_cases.yaml
             trigger          spec PDF, generates YAML     
                              test cases                   

  8          After all steps  Docker images + Python       Artifacts in
                              packages promoted via GHCR   GHCR/GitHub Packages
                              with manual approval gate    
  ------------------------------------------------------------------------------

**3.3 Infrastructure Layout**

-   Oracle Cloud Free Tier: 2x AMD VM (1 OCPU, 1GB RAM each) --- runs
    k3s cluster

-   k3s: Lightweight Kubernetes --- all platform services deployed as
    Pods

-   Terraform: Provisions Oracle VM, installs k3s via cloud-init,
    creates namespaces and secrets

-   MinIO: Deployed as a Pod on k3s --- S3-compatible storage for logs,
    models, reports

-   Prometheus + Grafana: Deployed as Pods --- scrape pipeline metrics,
    display dashboard

-   ChromaDB: Deployed as a Pod --- persistent vector store for ECU
    fault knowledge base

-   GitHub Actions: All CI/CD runs in GitHub-hosted runners (free for
    public repos)

**4. Component Deep Dive**

**4.1 Signal Simulator**

Generates realistic synthetic ECU diagnostic data mimicking UDS service
responses and OBD-II PID readings. Fault injection inserts known failure
patterns (e.g., NRC 0x22 conditionsNotCorrect, timeout sequences,
out-of-range sensor values).

  -----------------------------------------------------------------------
  **Module**            **Description**
  --------------------- -------------------------------------------------
  uds_simulator.py      Generates UDS service 0x22 (ReadDataByIdentifier)
                        response sequences with configurable fault rate

  obd_simulator.py      Generates OBD-II PID responses (RPM, coolant
                        temp, O2 sensors) with injected anomalies

  can_encoder.py        Encodes signal sequences into CAN frame format
                        using cantools DBC definitions

  fault_injector.py     Randomly injects fault patterns into signal
                        streams at configurable frequency

  dataset_writer.py     Writes output to Parquet format with signal ID,
                        timestamp, value, and fault label columns
  -----------------------------------------------------------------------

**4.2 Test Runner**

Executes YAML-defined test cases against the signal log. Test cases
specify expected signal ranges, response codes, and timing constraints.
Outputs structured JSON with pass/fail status, actual vs expected
values, and execution time per test.

  -----------------------------------------------------------------------
  **Module**            **Description**
  --------------------- -------------------------------------------------
  test_loader.py        Parses MTF-compatible YAML test case definitions

  signal_matcher.py     Matches test case assertions against signal log
                        entries by service ID and timestamp window

  result_writer.py      Writes test_results.json with status, delta, and
                        error message per test case

  conftest.py           pytest fixtures for loading signal log and test
                        case YAML
  -----------------------------------------------------------------------

**4.3 Anomaly Detector**

Trains an Isolation Forest model on normal ECU signal distributions. At
inference time, scores each signal sequence and flags outliers. Model is
serialized to MinIO after training and loaded for inference in
subsequent pipeline runs.

  ------------------------------------------------------------------------
  **Module**             **Description**
  ---------------------- -------------------------------------------------
  feature_extractor.py   Extracts statistical features per signal
                         sequence: mean, std, min, max, response_time_ms

  trainer.py             Trains Isolation Forest on normal (non-fault)
                         sequences; saves model to MinIO as .pkl

  detector.py            Loads model from MinIO; scores test-run signal
                         log; outputs anomaly_report.json

  evaluator.py           Computes precision/recall against fault_label
                         ground truth; logs metrics to Prometheus
  ------------------------------------------------------------------------

**4.4 AI Agent --- Root Cause Analysis**

A LangChain agent with three tools: a log reader tool, an anomaly report
reader tool, and a ChromaDB retrieval tool. The agent is given a failing
test case and instructed to reason step-by-step toward a root cause and
remediation suggestion.

  -----------------------------------------------------------------------
  **Component**         **Description**
  --------------------- -------------------------------------------------
  ChromaDB knowledge    Pre-populated with 50+ known ECU fault patterns,
  base                  NRC code descriptions, and historical RCA
                        examples as vector embeddings

  log_reader_tool       LangChain tool that reads test_results.json and
                        formats failing test data for the agent

  anomaly_tool          LangChain tool that reads anomaly_report.json and
                        returns anomaly score + feature deltas for a
                        given signal ID

  kb_retrieval_tool     LangChain tool that queries ChromaDB for the
                        top-3 most similar historical fault patterns

  rca_agent.py          ReAct-style LangChain agent that calls the three
                        tools and synthesizes a structured RCA markdown
                        report

  report_writer.py      Posts RCA report to GitHub Actions job summary
                        via GITHUB_STEP_SUMMARY; stores in MinIO
  -----------------------------------------------------------------------

**4.5 Test Case Generator**

Reads an ECU specification PDF (UDS or OBD-II spec document), chunks it
into sections, embeds into ChromaDB, and uses an LLM to generate new
test cases in MTF-compatible YAML format. Generated test cases are
committed back to the repo via a GitHub Actions step.

  -------------------------------------------------------------------------
  **Module**              **Description**
  ----------------------- -------------------------------------------------
  pdf_ingester.py         Uses PyMuPDF to extract text from ECU spec PDF;
                          splits into chunks by section heading

  spec_embedder.py        Embeds chunks into a separate ChromaDB collection
                          for spec RAG

  testcase_generator.py   LangChain chain that retrieves relevant spec
                          sections and prompts GPT-4o to generate YAML test
                          cases

  yaml_validator.py       Validates generated YAML against MTF test case
                          schema before committing

  auto_commit.py          Uses GitHub API (PyGithub) to commit generated
                          test cases to a new branch and open a PR
  -------------------------------------------------------------------------

**5. CI/CD Pipeline Design**

**5.1 GitHub Actions Workflows**

  ------------------------------------------------------------------------
  **Workflow File**    **Trigger**         **Jobs**
  -------------------- ------------------- -------------------------------
  pipeline.yml         Push to main, daily simulate → test → detect →
                       cron at 00:00 UTC   analyze → report

  build.yml            Push to main        Build all service Docker
                                           images, push to GHCR

  promote.yml          Manual dispatch     Promote images from dev tag to
                                           prod tag in GHCR, requires
                                           reviewer approval

  generate-tests.yml   Manual dispatch     Run test case generator, open
                       (with PDF input)    PR with new YAML test cases

  train-model.yml      Manual dispatch or  Retrain Isolation Forest, push
                       weekly cron         new model to MinIO

  terraform.yml        Push to infra/      Terraform plan on PR, terraform
                       directory           apply on merge to main
  ------------------------------------------------------------------------

**5.2 Artifact Promotion Flow**

-   Every push to main builds Docker images tagged with git SHA and
    pushed to GHCR

-   Images are also tagged :dev automatically on every successful build

-   promote.yml requires manual approval via GitHub Environments before
    tagging :prod

-   Python packages (simulator, detector, agent) published to GitHub
    Packages on version tag push

-   All promotion events logged as GitHub Actions job summaries

**5.3 Quality Gates**

-   Ruff linting --- enforced on all Python files before any pipeline
    step runs

-   MyPy type checking --- enforced on core modules (simulator,
    detector, agent)

-   pytest with \>80% coverage required before Docker build step
    proceeds

-   YAML schema validation on all generated test cases before PR is
    opened

-   Anomaly detector precision must be \>0.75 on training evaluation or
    pipeline fails

**6. Repository Structure**

  -----------------------------------------------------------------------
  **Path**                        **Purpose**
  ------------------------------- ---------------------------------------
  ecu-test-intelligence/          Monorepo root

  simulator/                      ECU signal simulator service

  uds_simulator.py                UDS response sequence generator

  obd_simulator.py                OBD-II PID response generator

  fault_injector.py               Fault injection logic

  Dockerfile                      Simulator container

  test_runner/                    Test execution service

  test_loader.py                  YAML test case parser

  signal_matcher.py               Assertion engine

  test_cases/                     MTF-format YAML test case definitions

  Dockerfile                      Test runner container

  anomaly_detector/               ML anomaly detection service

  trainer.py                      Isolation Forest training

  detector.py                     Inference and scoring

  feature_extractor.py            Signal feature engineering

  Dockerfile                      Detector container

  ai_agent/                       LangChain RCA agent service

  rca_agent.py                    ReAct agent with 3 tools

  kb_builder.py                   ChromaDB knowledge base population

  report_writer.py                RCA report formatter and publisher

  Dockerfile                      Agent container

  test_generator/                 LLM test case generation service

  pdf_ingester.py                 ECU spec PDF parser

  testcase_generator.py           LLM test case synthesis chain

  yaml_validator.py               MTF schema validator

  Dockerfile                      Generator container

  terraform/                      Infrastructure as Code

  modules/oracle_vm/              Oracle Cloud VM provisioning

  modules/k3s/                    k3s install via cloud-init

  modules/minio/                  MinIO deployment on k3s

  main.tf / variables.tf /        Root module
  outputs.tf                      

  k8s/                            Kubernetes manifests

  deployments/                    One Deployment per service

  configmaps/                     Environment config per service

  monitoring/                     Prometheus + Grafana manifests

  .github/workflows/              All GitHub Actions workflow files

  docker-compose.yml              Local development environment

  README.md                       Setup, architecture, and demo guide
  -----------------------------------------------------------------------

**7. Build Phases**

**Phase 1 --- Signal Simulator (Foundation)**

Build this first. Everything else depends on having realistic signal
data.

  ------------------------------------------------------------------------
  **Task**                             **Details**               **Est.
                                                                 Hours**
  ------------------------------------ ------------------------- ---------
  Setup repo + Docker Compose          Create monorepo, add      1h
                                       docker-compose.yml for    
                                       local dev                 

  UDS simulator                        Generate 1000 UDS 0x22    3h
                                       sequences with            
                                       configurable fault rate   

  OBD-II simulator                     Generate RPM, coolant     2h
                                       temp, O2 PID sequences    
                                       with anomalies            

  Fault injector                       10% fault injection rate: 2h
                                       NRC errors, timeouts,     
                                       out-of-range values       

  Parquet writer + pytest              Write output, add unit    2h
                                       tests, Ruff + MyPy        
                                       passing                   
  ------------------------------------------------------------------------

**Phase 2 --- Test Runner**

  ------------------------------------------------------------------------
  **Task**                             **Details**               **Est.
                                                                 Hours**
  ------------------------------------ ------------------------- ---------
  YAML test case schema                Define MTF-compatible     2h
                                       schema: service_id,       
                                       expected_response,        
                                       tolerance                 

  Write 20 sample test cases           Cover normal + fault      2h
                                       scenarios for both UDS    
                                       and OBD                   

  Signal matcher                       Match test assertions     3h
                                       against signal log by     
                                       service ID + time window  

  Result writer + pytest               Structured JSON output    2h
                                       with pass/fail/delta per  
                                       case                      
  ------------------------------------------------------------------------

**Phase 3 --- Anomaly Detector**

  ------------------------------------------------------------------------
  **Task**                             **Details**               **Est.
                                                                 Hours**
  ------------------------------------ ------------------------- ---------
  Feature extractor                    5 statistical features    2h
                                       per signal: mean, std,    
                                       min, max,                 
                                       response_time_ms          

  Isolation Forest trainer             Train on normal           3h
                                       sequences, serialize      
                                       model to local MinIO      

  Inference pipeline                   Load model, score         2h
                                       test-run log, output      
                                       anomaly_report.json       

  Evaluation metrics                   Precision/recall against  2h
                                       fault_label ground truth  

  MinIO setup (local)                  Run MinIO as Docker       1h
                                       container for local dev   
                                       storage                   
  ------------------------------------------------------------------------

**Phase 4 --- AI Agent (RCA)**

  ------------------------------------------------------------------------
  **Task**                             **Details**               **Est.
                                                                 Hours**
  ------------------------------------ ------------------------- ---------
  ChromaDB knowledge base              Populate with 50 ECU      3h
                                       fault patterns, NRC code  
                                       descriptions, sample RCAs 

  LangChain tools                      Implement                 3h
                                       log_reader_tool,          
                                       anomaly_tool,             
                                       kb_retrieval_tool         

  ReAct agent                          Wire tools into LangChain 3h
                                       ReAct agent with          
                                       structured output         

  Report writer                        Format RCA as markdown,   2h
                                       post to                   
                                       GITHUB_STEP_SUMMARY,      
                                       store in MinIO            

  End-to-end test                      Run full sim → test →     2h
                                       detect → agent chain      
                                       locally                   
  ------------------------------------------------------------------------

**Phase 5 --- Test Case Generator**

  ------------------------------------------------------------------------
  **Task**                             **Details**               **Est.
                                                                 Hours**
  ------------------------------------ ------------------------- ---------
  PDF ingester                         Parse UDS spec PDF        2h
                                       (publicly available ISO   
                                       14229 summary doc) into   
                                       chunks                    

  Spec embedder                        Embed chunks into         1h
                                       ChromaDB spec collection  

  LLM generation chain                 RAG chain: retrieve spec  3h
                                       sections → prompt GPT-4o  
                                       → output YAML test cases  

  YAML validator                       Validate against MTF      2h
                                       schema, reject malformed  
                                       output                    

  Auto PR via GitHub API               Commit generated YAML to  2h
                                       new branch, open draft PR 
  ------------------------------------------------------------------------

**Phase 6 --- DevOps & Infrastructure**

  ------------------------------------------------------------------------
  **Task**                             **Details**               **Est.
                                                                 Hours**
  ------------------------------------ ------------------------- ---------
  Dockerize all services               Write Dockerfile per      3h
                                       service, build and push   
                                       to GHCR                   

  GitHub Actions pipeline.yml          Wire all 5 pipeline steps 3h
                                       as dependent jobs         

  Build + promote workflows            build.yml, promote.yml    2h
                                       with GHCR and GitHub      
                                       Environments approval     

  Terraform Oracle VM                  Provision free-tier VM,   4h
                                       install k3s via           
                                       cloud-init                

  Kubernetes manifests                 Deployments for all       4h
                                       services + MinIO +        
                                       Prometheus + Grafana      

  Grafana dashboard                    Import pipeline metrics:  2h
                                       test pass rate, anomaly   
                                       rate, agent latency       

  README + demo recording              Architecture diagram in   3h
                                       README, screen-record one 
                                       full pipeline run         
  ------------------------------------------------------------------------

**8. Estimated Timeline**

  ------------------------------------------------------------------------
  **Phase**                   **Effort**            **Cumulative**
  --------------------------- --------------------- ----------------------
  Phase 1 --- Signal          10 hours              10h
  Simulator                                         

  Phase 2 --- Test Runner     9 hours               19h

  Phase 3 --- Anomaly         10 hours              29h
  Detector                                          

  Phase 4 --- AI Agent (RCA)  13 hours              42h

  Phase 5 --- Test Case       10 hours              52h
  Generator                                         

  Phase 6 --- DevOps &        21 hours              73h
  Infrastructure                                    

  Total                       \~70-75 hours         \~6-8 weeks at
                                                    10h/week
  ------------------------------------------------------------------------

*Recommended approach: complete Phases 1-3 first --- these are
self-contained, require no API keys, and produce a working demo. Phases
4-5 require an OpenAI API key (\~\$2-5 total cost for dev usage). Phase
6 requires the Oracle Cloud free account.*

**9. Resume Talking Points**

After project completion, add these as bullet points under a Projects
section:

-   Built a full-stack Automotive ECU Test Intelligence Platform
    combining CI/CD, ML anomaly detection, and LLM-based agentic
    automation

-   Implemented an Isolation Forest anomaly detector on synthetic
    UDS/OBD-II ECU signal data achieving \>80% precision on fault
    detection

-   Developed a LangChain ReAct agent that performs automated root cause
    analysis on ECU test failures using RAG over a ChromaDB fault
    knowledge base

-   Built an LLM-powered test case generator that parses ECU
    specification PDFs and produces MTF-compatible YAML test cases via a
    RAG pipeline

-   Deployed all services as Kubernetes workloads on k3s (Oracle Cloud
    free tier) provisioned with Terraform

-   Designed a GitHub Actions CI/CD pipeline with quality gates (Ruff,
    MyPy, pytest \>80% coverage) and GHCR-based artifact promotion with
    manual approval gates

-   Integrated Prometheus and Grafana for real-time monitoring of
    pipeline health, anomaly detection rates, and AI agent response
    latency

**10. Prerequisites & Cost**

  ------------------------------------------------------------------------
  **Item**              **Action**                        **Cost**
  --------------------- --------------------------------- ----------------
  GitHub account        Already have --- create public    Free
                        repo: ecu-test-intelligence       

  Oracle Cloud account  Sign up at oracle.com/cloud/free  Free
                        --- always-free tier, no expiry   

  OpenAI API key        sign up at platform.openai.com    \~\$3-5 total
                        --- only needed for Phases 4 and  
                        5                                 

  Docker Desktop        Install locally for building and  Free
                        testing images                    

  Python 3.11+          Confirm: python \--version        Free

  Terraform CLI v1.6+   Install via tfenv or direct       Free
                        download                          

  kubectl               Install for interacting with k3s  Free
                        cluster                           

  k3sup (optional)      Simplifies k3s install on Oracle  Free
                        VM: k3sup.dev                     
  ------------------------------------------------------------------------

**Total infrastructure cost: \~\$3-5 one-time for OpenAI API usage
during development. Everything else is permanently free.**
