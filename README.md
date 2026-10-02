# Enterprise MLOps Production Platform & Continuous Pipeline

A complete, production-grade enterprise MLOps platform for **Customer Churn Prediction** demonstrating end-to-end data version control, experiment tracking, pipeline orchestration, REST API microservice deployment, CI/CD automation, Prometheus/Grafana monitoring, Responsible AI auditing, and AWS cloud integration.

---

## 🏛️ System Architecture

```
                                  +-----------------------+
                                  |   Raw Data Ingestion  |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | Schema & Quality Check| (DataValidator)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | Data Preprocessing &  | (ColumnTransformer,
                                  | Feature Engineering   |  StandardScaler, OHE)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | MLflow Experiment     | (Baseline: LogisticRegression
                                  | Tracking & Training   |  Candidates: RF, GradientBoosting)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  | Quality Gate Check &  | (F1 >= 0.75, ROC-AUC >= 0.82)
                                  | MLflow Model Registry | -> Alias: 'Production'
                                  +-----------+-----------+
                                              |
              +-------------------------------+-------------------------------+
              |                                                               |
              v                                                               v
+-------------+-------------+                                   +-------------+-------------+
|  FastAPI Prediction REST  |                                   |  Apache Airflow DAG Suite   |
|  (Swagger UI @ :8000)     |                                   |  (Weekly Auto Re-training)  |
+-------------+-------------+                                   +---------------------------+
              |
              v
+-------------+-------------+
| Prometheus & Grafana      | (p95 Latency, Requests, Error Rate,
| Real-time Monitoring      |  KS-test Data Drift Ratio @ :3000)
+---------------------------+
```

---

## 🚀 One-Command Quick Start

To execute the entire end-to-end pipeline (Data Ingestion ➔ Validation ➔ Preprocessing ➔ MLflow Training ➔ Quality Gate ➔ Test Suite ➔ Drift Audit) run:

```bash
python run_all_mlops.py
```

To spin up the Dockerized Microservices Infrastructure (FastAPI REST API + Prometheus + Grafana):

```bash
docker-compose up --build
```

---

## 📋 Comprehensive Requirements Mapping (8 Pillars)

### 1. Version Control and Reproducibility
- **Git & DVC**: Data versioning configured with [`.dvc/config`](file:///c:/MLOPS_project/.dvc/config), [`dvc.yaml`](file:///c:/MLOPS_project/dvc.yaml), and [`params.yaml`](file:///c:/MLOPS_project/params.yaml).
- **Reproducibility**: Enforced via global fixed random seed `SEED = 42` across Python, NumPy, and Scikit-Learn in [`src/config.py`](file:///c:/MLOPS_project/src/config.py).
- **Environment**: Locked dependencies specified in [`requirements.txt`](file:///c:/MLOPS_project/requirements.txt).

### 2. Experiment Management & MLflow Model Registry
- **Experiment Tracking**: Managed via MLflow (`mlflow.set_tracking_uri`). Logs parameters, metrics (Accuracy, Precision, Recall, F1, ROC-AUC), and artifacts across 1 Baseline (`LogisticRegression`) and 2 Candidate models (`RandomForestClassifier`, `GradientBoostingClassifier`).
- **Model Registry**: Champion model automatically registered under `CustomerChurnPredictor` with model versioning, metadata tags, and the `Production` alias in [`src/models/train.py`](file:///c:/MLOPS_project/src/models/train.py).

### 3. Automated ML Workflow (Apache Airflow)
- **Airflow DAG**: Defined in [`dags/mlops_pipeline_dag.py`](file:///c:/MLOPS_project/dags/mlops_pipeline_dag.py) covering data ingestion, schema validation, preprocessing, feature engineering, training, quality gate evaluation, and model registration.

### 4. REST Service Deployment (FastAPI + Docker)
- **FastAPI REST API**: [`app/main.py`](file:///c:/MLOPS_project/app/main.py) with Pydantic request/response validation schemas in [`app/schemas.py`](file:///c:/MLOPS_project/app/schemas.py).
- **Endpoints**:
  - `GET /health` - Health & liveness status.
  - `GET /ready` - Model readiness probe.
  - `GET /model-info` - Active registered model metadata.
  - `POST /predict` - Single record prediction with latency & risk level (`LOW`, `MEDIUM`, `HIGH`).
  - `POST /predict-batch` - Array batch prediction.
  - `POST /explain` - Real-time SHAP feature attributions.
  - `POST /drift-check` - Real-time statistical data drift check.
  - `GET /metrics` - Prometheus metrics scraper endpoint.
- **Docker**: Multi-stage [`Dockerfile`](file:///c:/MLOPS_project/Dockerfile) & [`docker-compose.yml`](file:///c:/MLOPS_project/docker-compose.yml) orchestrating API (Port 8000), Prometheus (Port 9090), and Grafana (Port 3000).

### 5. CI/CD and Quality Gates (GitHub Actions)
- **Workflow**: [`.github/workflows/ci_cd.yml`](file:///c:/MLOPS_project/.github/workflows/ci_cd.yml) runs on push/PR:
  - Dependency installation.
  - Pytest unit tests ([`tests/test_preprocessing.py`](file:///c:/MLOPS_project/tests/test_preprocessing.py), [`tests/test_prediction.py`](file:///c:/MLOPS_project/tests/test_prediction.py)) & API integration tests ([`tests/test_api.py`](file:///c:/MLOPS_project/tests/test_api.py)).
  - Quality gate threshold enforcement (F1 ≥ 0.75, ROC-AUC ≥ 0.82) in [`src/models/evaluate.py`](file:///c:/MLOPS_project/src/models/evaluate.py).
  - Docker container build test.

### 6. Monitoring & Data Drift
- **Prometheus & Grafana**: Live scraping configured in [`prometheus/prometheus.yml`](file:///c:/MLOPS_project/prometheus/prometheus.yml) & dashboard defined in [`grafana/dashboards/mlops_dashboard.json`](file:///c:/MLOPS_project/grafana/dashboards/mlops_dashboard.json).
- **Drift Engine**: Kolmogorov-Smirnov (KS) test & Wasserstein distance detector in [`src/monitoring/drift_detector.py`](file:///c:/MLOPS_project/src/monitoring/drift_detector.py).

### 7. Responsible AI & Governance
- **SHAP Explainability**: Implemented in [`src/responsible_ai/shap_explainer.py`](file:///c:/MLOPS_project/src/responsible_ai/shap_explainer.py) exposing positive and negative feature attributions.
- **Demographic Bias & Fairness Audit**: Demographic Parity & 80% Four-Fifths Disparate Impact rule auditor in [`src/responsible_ai/fairness_audit.py`](file:///c:/MLOPS_project/src/responsible_ai/fairness_audit.py).
- **Governance Cards**: [`MODEL_CARD.md`](file:///c:/MLOPS_project/MODEL_CARD.md), [`DATA_CARD.md`](file:///c:/MLOPS_project/DATA_CARD.md), and [`PERFORMANCE_REPORT.md`](file:///c:/MLOPS_project/PERFORMANCE_REPORT.md).

### 8. Cloud Extension (AWS Integration)
- **AWS Integration**: S3 artifact upload, SageMaker endpoint deployment simulation, and automated resource teardown script for cost control in [`src/cloud/aws_integration.py`](file:///c:/MLOPS_project/src/cloud/aws_integration.py).

---

## 🧪 Running the Pytest Suite

```bash
python -m pytest tests/ -v
```

---

## 📂 Key Files & Documentation Links

- **Main Orchestrator**: [`run_all_mlops.py`](file:///c:/MLOPS_project/run_all_mlops.py)
- **REST Service**: [`app/main.py`](file:///c:/MLOPS_project/app/main.py)
- **Model Card**: [`MODEL_CARD.md`](file:///c:/MLOPS_project/MODEL_CARD.md)
- **Data Card**: [`DATA_CARD.md`](file:///c:/MLOPS_project/DATA_CARD.md)
- **Performance Report**: [`PERFORMANCE_REPORT.md`](file:///c:/MLOPS_project/PERFORMANCE_REPORT.md)
