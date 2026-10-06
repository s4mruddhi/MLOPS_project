# Jenkins & GitHub CI/CD Pipeline Integration Guide

This guide details how **Jenkins connects to GitHub** and how the **CI/CD pipeline is configured, built, and executed** in this enterprise MLOps project.

---

## Part 1: Step-by-Step GitHub & Jenkins Connection

### Step 1: Generate a GitHub Personal Access Token (PAT)
1. Go to GitHub **Settings** → **Developer Settings** → **Personal Access Tokens** (Tokens Classic).
2. Click **Generate new token**.
3. Select scopes:
   - `repo` (Full control of repositories)
   - `admin:repo_hook` (Hook administration)
4. Copy and securely store the generated token string.

---

### Step 2: Add GitHub Credentials in Jenkins
1. Open Jenkins Dashboard → **Manage Jenkins** → **Credentials** → **System** → **Global credentials (unrestricted)**.
2. Click **Add Credentials**.
3. Configure the fields:
   - **Kind**: `Username with password`
   - **Username**: Your GitHub username (`s4mruddhi`)
   - **Password**: Paste your GitHub Personal Access Token (PAT)
   - **ID**: `github-credentials`
4. Click **Create** / **Save**.

---

### Step 3: Configure GitHub Webhook for Automatic Push Triggers
To automatically trigger the Jenkins pipeline whenever code is pushed:
1. In the GitHub repository (`s4mruddhi/MLOPS_project`), navigate to **Settings** → **Webhooks** → **Add webhook**.
2. **Payload URL**: `http://<YOUR_JENKINS_SERVER_IP>:8080/github-webhook/`
3. **Content type**: `application/json`
4. **Which events would you like to trigger this webhook?**: Select **Just the push event**.
5. Ensure **Active** is checked and click **Add webhook**.

---

### Step 4: Create & Link the Jenkins Pipeline Job
1. In Jenkins, click **New Item** → Enter name (e.g., `MLOPS_Pipeline`) → Select **Pipeline** → Click **OK**.
2. Under **Build Triggers**, check **GitHub hook trigger for GITScm polling**.
3. Under **Pipeline**:
   - **Definition**: Select `Pipeline script from SCM`
   - **SCM**: Select `Git`
   - **Repository URL**: `https://github.com/s4mruddhi/MLOPS_project.git`
   - **Credentials**: Select `github-credentials`
   - **Branch Specifier**: `*/main`
   - **Script Path**: `Jenkinsfile`
4. Click **Save**.

---

## Part 2: How the Pipeline is Built & Executed in this Project

The pipeline automation is declared in [`Jenkinsfile`](../Jenkinsfile). It automates document processing, vector indexing, experiment tracking, orchestration, drift audits, test verification, and containerization across 8 stages:

```
[ Git Checkout & Setup ] ➔ [ Document Validation & Chunking ] ➔ [ Vector Indexing & Evaluation ] 
       ➔ [ MLflow Tracking & Registration ] ➔ [ Airflow DAG Pipeline ] 
       ➔ [ REST API, Monitoring & Drift ] ➔ [ Pytest Integration Suite ] ➔ [ Docker Build ]
```

### Stage Breakdown in [`Jenkinsfile`](../Jenkinsfile):

1. **Checkout & Environment Setup** ([`Jenkinsfile:L12-L34`](../Jenkinsfile#L12-L34))
   Pulls latest code from GitHub and provisions dependencies from [`requirements.txt`](../requirements.txt):
   ```groovy
   git branch: 'main', url: 'https://github.com/s4mruddhi/MLOPS_project.git'
   pip3 install --break-system-packages -r requirements.txt || pip install -r requirements.txt
   ```

2. **Phase 4: Document Validation & Chunking** ([`Jenkinsfile:L36-L43`](../Jenkinsfile#L36-L43))
   Validates schema structure across documents and chunks text into embeddings-ready segments:
   ```bash
   python scripts/run_phase4_pipeline.py
   ```

3. **Phase 5 & 7: Vector Indexing & Retrieval Evaluation** ([`Jenkinsfile:L45-L53`](../Jenkinsfile#L45-L53))
   Embeds chunks into ChromaDB vector store and evaluates baseline retrieval (TF-IDF vs BM25 vs Semantic):
   ```bash
   python scripts/run_phase5_pipeline.py
   python scripts/run_phase7_evaluation.py
   ```

4. **Phase 8 & 10: MLflow Tracking & RAG Evaluation** ([`Jenkinsfile:L55-L63`](../Jenkinsfile#L55-L63))
   Logs experiments and registers the Champion model in the MLflow Model Registry (`RAGOps_Retrieval_Champion`), then runs the groundedness & citation evaluation:
   ```bash
   python scripts/run_phase8_mlflow.py
   python scripts/run_phase10_evaluation.py
   ```

5. **Phase 11: Airflow DAG Pipeline Execution** ([`Jenkinsfile:L65-L72`](../Jenkinsfile#L65-L72))
   Executes all 11 Airflow DAG tasks sequentially through automated quality gates:
   ```bash
   python scripts/run_phase11_pipeline.py
   ```

6. **Phase 12, 14 & 15: REST API, Monitoring & Drift Audits** ([`Jenkinsfile:L74-L83`](../Jenkinsfile#L74-L83))
   Validates FastAPI microservice endpoints, verifies Prometheus metrics/alerts, and executes Kolmogorov-Smirnov drift tests:
   ```bash
   python scripts/run_phase12_pipeline.py
   python scripts/run_phase14_monitoring.py
   python scripts/run_phase15_drift.py
   ```

7. **Run Pytest Integration Suite** ([`Jenkinsfile:L85-L92`](../Jenkinsfile#L85-L92))
   Runs 81 integration and unit tests covering every pipeline phase:
   ```bash
   PYTHONPATH=. python -m pytest tests/ -v
   ```

8. **Phase 13: Docker Image Build** ([`Jenkinsfile:L94-L101`](../Jenkinsfile#L94-L101))
   Packages the microservice into a production container:
   ```bash
   docker build -t ragops-assistant-api:latest .
   ```

---

## Local Validation Summary

All stages were locally validated in the project environment:
- **Phase 4**: 27 documents validated, 78 chunks produced in 0.06s.
- **Phase 5**: 78 vectors indexed into ChromaDB with `all-MiniLM-L6-v2`.
- **Phase 7**: Retrieval benchmark evaluated (Recall@3: 0.9722, MRR@3: 0.9722).
- **Phase 8**: MLflow experiment runs tracked & registered `RAGOps_Retrieval_Champion` (version 2).
- **Phase 10**: Groundedness (0.9574), Answer Relevance (0.7418), 100% Citation Rate across golden test set.
- **Phase 11**: All 11 Airflow DAG tasks succeeded.
- **Phase 12**: FastAPI `/health`, `/version`, `/query`, `/documents`, `/metrics`, and `/admin/*` verified.
- **Phase 14**: Prometheus alert rules and Grafana dashboard panels validated.
- **Phase 15**: In-domain (0.0251 distance, no drift) and Out-of-domain (0.8271 distance, drift detected) verified.
- **Stage 7 (Pytest)**: **81 of 81 tests passed (100%)**.
