# Production-Ready Enterprise Knowledge Assistant (RAG Ops) with Continuous Evaluation

A complete, production-grade enterprise **RAG Ops & Knowledge Assistant Platform** demonstrating data version control, experiment tracking, pipeline orchestration, REST API microservice deployment, CI/CD automation, Prometheus/Grafana monitoring, Responsible AI citation entailment auditing, and AWS cloud integration.

---

## 🏛️ System Architecture

```
                                  +-----------------------+
                                  | Knowledge Base Docs   | (SOC2, GDPR, API Gateway Specs,
                                  | Ingestion             |  PostgreSQL Runbooks)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | Schema & Quality Check| (DataValidator)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | Document Chunking &   | (RAGVectorPreprocessor,
                                  | Vector Embeddings     |  Dense/Hybrid Indexes)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | MLflow Experiment     | (Baseline: Sparse TF-IDF
                                  | Tracking & Benchmarking|  Candidates: Dense & Reranked Agentic RAG)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | Quality Gate Check &  | (ContextPrec >= 75%, CitationPrec >= 80%)
                                  | MLflow Model Registry | -> Alias: 'Production'
                                  +-----------+-----------+
                                              |
              +-------------------------------+-------------------------------+
              |                                                               |
              v                                                               v
+-------------+-------------+                                   +-------------+-------------+
|  FastAPI REST Service     |                                   |  Apache Airflow DAG Suite   |
|  & Interactive RAG UI     |                                   |  (Weekly Auto Re-indexing)  |
|  (Dashboard @ :8000)      |                                   |  (dags/mlops_pipeline_dag)  |
+-------------+-------------+                                   +---------------------------+
              |
              v
+-------------+-------------+
| Prometheus & Grafana      | (p95 Latency, Query Count, Error Rate,
| Live Monitoring           |  KS-test Query Drift Ratio @ :3000)
+---------------------------+
```

---

## 🚀 One-Command Quick Start

To execute the complete end-to-end pipeline (Document Ingestion ➔ Validation ➔ Chunk Vector Indexing ➔ MLflow RAG Evaluation ➔ Quality Gate ➔ Test Suite ➔ Query Drift Audit) run:

```bash
python run_all_mlops.py
```

To start the FastAPI REST API & Interactive RAG Assistant UI:

```bash
uvicorn app.main:app --port 8000
```
Then open **`http://localhost:8000`** in your browser!

---

## 📋 Comprehensive Requirements Mapping (8 Pillars)

### 1. Version Control & Reproducibility
- **Git & DVC**: Document corpus & vector index pointers tracked via [`.dvc/config`](file:///c:/MLOPS_project/.dvc/config), [`dvc.yaml`](file:///c:/MLOPS_project/dvc.yaml), and [`params.yaml`](file:///c:/MLOPS_project/params.yaml).
- **Reproducibility**: Enforced via global fixed random seed `SEED = 42` across Python, NumPy, and Scikit-Learn in [`src/config.py`](file:///c:/MLOPS_project/src/config.py).
- **Environment**: Locked dependencies specified in [`requirements.txt`](file:///c:/MLOPS_project/requirements.txt).

### 2. Experiment Management & MLflow Model Registry
- **MLflow Tracking**: Managed via MLflow (`mlflow.set_tracking_uri`). Logs parameters, Context Precision, Citation Precision, Faithfulness, and Latency across 1 Baseline (`SparseRetriever`) and 2 Candidate RAG models (`DenseVector_RAG`, `Reranked_AgenticRAG`) in [`src/models/train.py`](file:///c:/MLOPS_project/src/models/train.py).
- **Model Registry**: Champion RAG model automatically registered under `EnterpriseRAGAssistant` with versioning, quality gate tag, and the `Production` alias.

### 3. Automated ML Workflow (Apache Airflow)
- **Airflow DAG**: Defined in [`dags/mlops_pipeline_dag.py`](file:///c:/MLOPS_project/dags/mlops_pipeline_dag.py) covering document ingestion, schema validation, chunk preprocessing, vector indexing, evaluation, quality gate check, and RAG engine registration.

### 4. REST Service Deployment (FastAPI + Docker)
- **FastAPI REST API**: [`app/main.py`](file:///c:/MLOPS_project/app/main.py) with Pydantic request/response validation schemas in [`app/schemas.py`](file:///c:/MLOPS_project/app/schemas.py).
- **Endpoints**:
  - `GET /` - Interactive Enterprise Knowledge Assistant & RAG Dashboard UI.
  - `GET /health` - Health & liveness status.
  - `GET /ready` - Model readiness probe.
  - `GET /model-info` - Active production RAG model metadata.
  - `POST /ask` or `POST /predict` - Enterprise knowledge query with inline citations `[DOC-XXX]`.
  - `POST /predict-batch` - Array batch queries.
  - `POST /explain` - Real-time NLI claim-level citation verification & evidence attributions.
  - `POST /drift-check` - Query distribution drift test.
  - `GET /metrics` - Prometheus metrics scraper endpoint.
- **Docker**: Multi-stage [`Dockerfile`](file:///c:/MLOPS_project/Dockerfile) & [`docker-compose.yml`](file:///c:/MLOPS_project/docker-compose.yml) orchestrating API (Port 8000), Prometheus (Port 9090), and Grafana (Port 3000).

### 5. CI/CD and Quality Gates (GitHub Actions)
- **Workflow**: [`.github/workflows/ci_cd.yml`](file:///c:/MLOPS_project/.github/workflows/ci_cd.yml) runs on push/PR:
  - Dependency installation.
  - Pytest unit tests ([`tests/test_preprocessing.py`](file:///c:/MLOPS_project/tests/test_preprocessing.py), [`tests/test_prediction.py`](file:///c:/MLOPS_project/tests/test_prediction.py)) & API integration tests ([`tests/test_api.py`](file:///c:/MLOPS_project/tests/test_api.py)).
  - Quality gate threshold enforcement (Context Precision ≥ 75%, Citation Precision ≥ 80%) in [`src/models/evaluate.py`](file:///c:/MLOPS_project/src/models/evaluate.py).
  - Docker container build test.

### 6. Monitoring & Data Drift
- **Prometheus & Grafana**: Live scraping configured in [`prometheus/prometheus.yml`](file:///c:/MLOPS_project/prometheus/prometheus.yml) & dashboard defined in [`grafana/dashboards/mlops_dashboard.json`](file:///c:/MLOPS_project/grafana/dashboards/mlops_dashboard.json).
- **Query Drift Engine**: Kolmogorov-Smirnov (KS-test) & Wasserstein distance query distribution detector in [`src/monitoring/drift_detector.py`](file:///c:/MLOPS_project/src/monitoring/drift_detector.py).

### 7. Responsible AI & Governance
- **Citation Entailment Verification**: Implemented in [`src/responsible_ai/shap_explainer.py`](file:///c:/MLOPS_project/src/responsible_ai/shap_explainer.py) and [`eval_engine/citation_verifier.py`](file:///c:/MLOPS_project/eval_engine/citation_verifier.py) checking sentence-level claim support (`ENTAILED` vs `UNSUPPORTED`).
- **Demographic Bias & Fairness Audit**: Evaluator in [`src/responsible_ai/fairness_audit.py`](file:///c:/MLOPS_project/src/responsible_ai/fairness_audit.py).
- **Governance Cards**: [`MODEL_CARD.md`](file:///c:/MLOPS_project/MODEL_CARD.md), [`DATA_CARD.md`](file:///c:/MLOPS_project/DATA_CARD.md), and [`PERFORMANCE_REPORT.md`](file:///c:/MLOPS_project/PERFORMANCE_REPORT.md).

### 8. Cloud Extension (AWS Integration)
- **AWS Integration**: S3 document storage, SageMaker endpoint deployment simulation, and automated resource teardown script for cost control in [`src/cloud/aws_integration.py`](file:///c:/MLOPS_project/src/cloud/aws_integration.py).

---

## 🧪 Running the Pytest Suite

```bash
python -m pytest tests/ -v
```

---

## 📂 Key Files & Documentation Links

- **Main Orchestrator**: [`run_all_mlops.py`](file:///c:/MLOPS_project/run_all_mlops.py)
- **RAG Benchmark Evaluator**: [`run_benchmark.py`](file:///c:/MLOPS_project/run_benchmark.py)
- **REST Service**: [`app/main.py`](file:///c:/MLOPS_project/app/main.py)
- **Model Card**: [`MODEL_CARD.md`](file:///c:/MLOPS_project/MODEL_CARD.md)
- **Data Card**: [`DATA_CARD.md`](file:///c:/MLOPS_project/DATA_CARD.md)
- **Performance Report**: [`PERFORMANCE_REPORT.md`](file:///c:/MLOPS_project/PERFORMANCE_REPORT.md)
