# 5-Minute Academic Demonstration & Viva Presentation Script

## Project Title: RAGOps: Monitored Enterprise Knowledge Assistant

---

### 🕒 Live Demonstration Sequence (5 Minutes)

| Timestamp | Presentation Phase | Action & Screencast Instruction |
| :--- | :--- | :--- |
| **00:00 - 00:30** | **1. Problem Statement & Architecture** | Explain the core problem: Building a monitored enterprise Knowledge Assistant that answers employee support questions using **only verified organizational documents**. Show architecture diagram in [`docs/architecture.md`](file:///c:/MLOPS_project/docs/architecture.md). |
| **00:30 - 01:00** | **2. Verified Docs & DVC Versioning** | Open [`data/raw/knowledge_docs.json`](file:///c:/MLOPS_project/data/raw/knowledge_docs.json) showing SOC2 policies, API specs, and PostgreSQL runbooks with metadata tags (`document_id`, `version`, `effective_date`). Show DVC tracking via [`dvc.yaml`](file:///c:/MLOPS_project/dvc.yaml). |
| **01:00 - 01:40** | **3. Live RAG Q&A Assistant UI** | Open **`http://localhost:8000`**. Ask: *"What is the maximum allowed API request payload size according to gateway docs?"* Click **Execute RAG Retrieval & Generation**. |
| **01:40 - 02:20** | **4. Citations & Groundedness** | Point out retrieved chunk sources `[DOC-GATEWAY-101]`, NLI claim entailment verification status (`ENTAILED`), and latency metrics. Show unanswerable question handling (*"What is the private jet reimbursement policy?"* ➔ *"I could not find sufficient information..."*). |
| **02:20 - 02:50** | **5. MLflow Experiment Tracking** | Show MLflow tracking runs comparing Sparse TF-IDF (Baseline), Dense Vector (Candidate 1), and Reranked Agentic RAG (Champion). Show registered model `EnterpriseRAGAssistant` with `Production` alias. |
| **02:50 - 03:15** | **6. Apache Airflow Pipeline DAG** | Open [`dags/mlops_pipeline_dag.py`](file:///c:/MLOPS_project/dags/mlops_pipeline_dag.py) demonstrating automated ingestion ➔ validation ➔ chunking ➔ vector indexing ➔ quality gate check. |
| **03:15 - 03:30** | **7. FastAPI REST API & Swagger** | Open **`http://localhost:8000/docs`**. Show Pydantic schemas, `/ask`, `/explain`, `/drift-check`, `/health`, and `/metrics`. |
| **03:30 - 03:45** | **8. Docker Containerization** | Open [`Dockerfile`](file:///c:/MLOPS_project/Dockerfile) and [`docker-compose.yml`](file:///c:/MLOPS_project/docker-compose.yml). |
| **03:45 - 04:10** | **9. Prometheus & Grafana Monitoring** | Open Grafana at **`http://localhost:3000`**. Show live query volume, p95 query latency, error rates, and groundedness metrics. |
| **04:10 - 04:30** | **10. Query Drift Detection (KS-Test)** | Click **Audit Query Distribution Drift** in UI showing Kolmogorov-Smirnov test results comparing incoming queries against reference baseline. |
| **04:30 - 05:00** | **11. AWS S3, SageMaker & Cleanup** | Show S3 bucket structure (`s3://ragops-bucket/`), SageMaker evaluation workload in [`scripts/sagemaker/train_or_evaluate.py`](file:///c:/MLOPS_project/scripts/sagemaker/train_or_evaluate.py), CloudWatch logging integration, and teardown cost-control instructions in [`scripts/aws/cleanup.md`](file:///c:/MLOPS_project/scripts/aws/cleanup.md). |
