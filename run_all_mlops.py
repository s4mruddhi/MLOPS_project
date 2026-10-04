"""
Master One-Command RAGOps Pipeline Orchestrator.
Executes document ingestion, validation, vector chunking, RAG generation, evaluation, Airflow pipeline, REST API tests, and monitoring load tests.
"""

import os
import sys

# Ensure environment flags set prior to torch/tf imports
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

def main():
    print("================================================================================")
    print("   ENTERPRISE KNOWLEDGE ASSISTANT (RAG OPS): AUTOMATED PIPELINE EXECUTOR      ")
    print("================================================================================")

    # 1. Phase 4: Validation & Preprocessing
    print("\n[STEP 1/7] Running Document Ingestion, Validation & Chunking Pipeline (Phase 4)...")
    from scripts.run_phase4_pipeline import run_pipeline as run_phase4
    run_phase4()

    # 2. Phase 5: ChromaDB Vector Indexing
    print("\n[STEP 2/7] Preprocessing Document Chunks & Vector Embedding Index (Phase 5)...")
    from scripts.run_phase5_pipeline import run_phase5
    run_phase5()

    # 3. Phase 7: Retrieval Evaluation
    print("\n[STEP 3/7] Evaluating Retrieval Engine Metrics (Phase 7)...")
    from scripts.run_phase7_evaluation import run_phase7
    run_phase7()

    # 4. Phase 8 & 10: MLflow Tracking & RAG Evaluation
    print("\n[STEP 4/7] Tracking MLflow Experiments & RAG Quality Gate (Phase 8 & 10)...")
    from scripts.run_phase8_mlflow import run_phase8
    from scripts.run_phase10_evaluation import run_phase10
    run_phase8()
    run_phase10()

    # 5. Phase 11: Airflow DAG Pipeline Simulation
    print("\n[STEP 5/7] Executing Airflow DAG Sequential Task Pipeline (Phase 11)...")
    from scripts.run_phase11_pipeline import run_phase11
    run_phase11()

    # 6. Phase 12 & 13: FastAPI REST Service & Docker Validation
    print("\n[STEP 6/7] Verifying FastAPI REST API & Docker Configurations (Phase 12 & 13)...")
    from scripts.run_phase12_pipeline import main as run_phase12
    from scripts.run_phase13_pipeline import main as run_phase13
    run_phase12()
    run_phase13()

    # 7. Phase 14: Prometheus & Grafana Monitoring & Alerting
    print("\n[STEP 7/8] Auditing Prometheus Metrics & Grafana Alert Rules (Phase 14)...")
    from scripts.run_phase14_monitoring import main as run_phase14
    run_phase14()

    # 8. Phase 15: Data & Query Drift Detection
    print("\n[STEP 8/9] Auditing Query & Embedding Distribution Drift Engine (Phase 15)...")
    from scripts.run_phase15_drift import main as run_phase15
    run_phase15()

    # 9. Phase 16: Responsible AI & Safety Guardrails
    print("\n[STEP 9/9] Auditing Prompt Injection, PII Redaction & Fairness Guardrails (Phase 16)...")
    from scripts.run_phase16_guardrails import main as run_phase16
    run_phase16()

    print("\n================================================================================")
    print("         ENTERPRISE RAG OPS PIPELINE EXECUTION SUCCESSFUL!                     ")
    print("================================================================================")
    print("\nTo launch MLflow UI:")
    print("  mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000\n")
    print("To launch FastAPI REST Service & Interactive RAG Dashboard UI:")
    print("  uvicorn app.main:app --host 0.0.0.0 --port 8000\n")
    print("To launch Docker Compose Stack (FastAPI + Prometheus + Grafana):")
    print("  docker compose up --build -d\n")

if __name__ == "__main__":
    main()
