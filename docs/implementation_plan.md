# RAGOps 22-Phase Implementation Roadmap & Strategy

## Phase 1: Architecture, Repository & Configuration (Current Phase)
- Setup clean project folder hierarchy (`app/`, `data/`, `dags/`, `configs/`, `prompts/`, `scripts/`, `docs/`, `tests/`, `monitoring/`).
- Create environment configurations ([`.env.example`](file:///c:/MLOPS_project/.env.example), [`requirements.txt`](file:///c:/MLOPS_project/requirements.txt)).
- CI/CD workflow definition ([`.github/workflows/ci_cd.yml`](file:///c:/MLOPS_project/.github/workflows/ci_cd.yml)).

## Phase 2: Synthetic Enterprise Documents & Metadata
- Generate verified organizational document corpus (HR policies, IT manuals, travel policies, product specs).
- Ensure mandatory metadata (`document_id`, `title`, `department`, `category`, `version`, `effective_date`, `source`, `access_level`).

## Phase 3: DVC + S3 Remote Setup
- Configure DVC tracking for `data/raw/` and `data/processed/`.
- Setup S3 remote storage pointer (`s3://<bucket>/dvc-artifacts/`).

## Phase 4: Document Validation & Preprocessing
- Implement pre-indexing validation rules (readability, file type, empty text, corrupted format, duplicate IDs).
- Implement configurable chunker (`chunk_size`, `chunk_overlap`).

## Phase 5: ChromaDB & Embedding Layer
- Initialize ChromaDB persistent vector store.
- Integrate configurable embedding model (`sentence-transformers/all-MiniLM-L6-v2`).

## Phase 6: Retrieval Approaches (TF-IDF, BM25, Semantic)
- Build Baseline retriever (TF-IDF).
- Build Candidate 1 retriever (BM25).
- Build Candidate 2 retriever (SentenceTransformer Semantic Vector).

## Phase 7: RAG Benchmark Dataset & Evaluation Metrics
- Create `data/evaluation/rag_questions.jsonl` (including unanswerable & ambiguous questions).
- Calculate Recall@K, Precision@K, MRR, Context Relevance.

## Phase 8: MLflow Experiments & Model Registry
- Log retrieval experiments, parameters, metrics, and artifacts to MLflow.
- Register champion retrieval engine under `EnterpriseRAGAssistant` with `Production` alias.

## Phase 9: RAG Generation & Prompt Versioning
- Implement versioned prompt system (`prompts/system_v1.txt`, `prompts/answer_v1.txt`).
- Grounded answer generation with inline citations (`[DOC-ID]`).

## Phase 10: Groundedness & Claim-Level Entailment Evaluation
- Calculate claim-to-source NLI entailment score.
- Handle unanswerable questions gracefully without hallucination.

## Phase 11: Apache Airflow Automation DAG
- Build `dags/mlops_pipeline_dag.py` covering ingestion ➔ validation ➔ chunking ➔ embedding ➔ vector indexing ➔ quality gate ➔ registration.

## Phase 12: FastAPI REST Service
- Build FastAPI endpoints (`GET /health`, `GET /version`, `POST /query`, `POST /explain`, `POST /drift-check`, `GET /metrics`).

## Phase 13: Docker & Docker Compose Setup
- Production multi-stage `Dockerfile` and `docker-compose.yml` (API, Prometheus, Grafana).

## Phase 14: Prometheus & Grafana Monitoring
- Expose `rag_*` metrics in Prometheus format.
- Provision Grafana dashboard for p95 latency, query volume, groundedness, and error rate.

## Phase 15: Drift Detection & Simulated Drift
- Implement Kolmogorov-Smirnov (KS-test) and PSI drift detector across query distributions.
- Generate `docs/drift_report.md`.

## Phase 16: CI/CD GitHub Actions & Test Suite
- Automate pytest unit tests, API integration tests, Docker build test, and Quality Gate check.

## Phase 17: AWS SageMaker Cloud Workload
- Create SageMaker evaluation/retrieval benchmark scripts (`scripts/sagemaker/`).

## Phase 18: AWS S3 Production Integration
- Configure S3 storage structure (`raw-documents/`, `dvc/`, `mlflow/`, `reports/`).

## Phase 19: AWS Application Deployment
- Document & script AWS EC2 / ECS application deployment.

## Phase 20: AWS CloudWatch Logging & Observability
- Configure structured CloudWatch application logging.

## Phase 21: Governance, Cards & Performance Report
- Write [`docs/data_card.md`](file:///c:/MLOPS_project/docs/data_card.md), [`docs/model_card.md`](file:///c:/MLOPS_project/docs/model_card.md), [`docs/responsible_ai.md`](file:///c:/MLOPS_project/docs/responsible_ai.md), [`docs/performance_report.md`](file:///c:/MLOPS_project/docs/performance_report.md).

## Phase 22: End-to-End Testing & 5-Minute Viva Demo Script
- Prepare [`docs/demo_script.md`](file:///c:/MLOPS_project/docs/demo_script.md) for 5-minute academic presentation.
