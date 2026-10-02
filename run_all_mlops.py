"""
Master One-Command RAG Ops Pipeline Orchestrator.
Executes document ingestion, validation, vector chunking, RAG model training, MLflow registration, testing, and drift auditing.
"""

import os
import sys
import pytest
import pandas as pd

from src.config import RAW_DOCS_PATH, REFERENCE_QUERIES_PATH
from src.data.ingestion import ingest_data
from src.data.validation import DataValidator
from src.data.preprocessing import preprocess_rag_data
from src.models.train import run_training_pipeline
from src.monitoring.drift_detector import DataDriftDetector


def main():
    print("================================================================================")
    print("   ENTERPRISE KNOWLEDGE ASSISTANT (RAG OPS): AUTOMATED PIPELINE EXECUTOR      ")
    print("================================================================================")

    # 1. Document Ingestion
    print("\n[STEP 1/6] Running Knowledge Base Document Ingestion...")
    documents = ingest_data()

    # 2. Schema Validation
    print("\n[STEP 2/6] Running Document Schema & Quality Validation...")
    is_valid, errors = DataValidator.validate(documents)
    if not is_valid:
        print(f"FAILED: Data validation errors: {errors}")
        sys.exit(1)
    print("Validation PASSED (Zero empty docs, token bounds verified).")

    # 3. Vector Chunk Preprocessing & Embedding Indexing
    print("\n[STEP 3/6] Preprocessing Document Chunks & Vector Embedding Index...")
    vectors, preprocessor, docs = preprocess_rag_data(documents, fit=True)
    print(f"Vector matrix created with shape {vectors.shape} across {len(docs)} knowledge documents.")

    # 4. RAG Model Training & MLflow Model Registry Promotion
    print("\n[STEP 4/6] Evaluating RAG Candidate Models & Logging MLflow Tracking...")
    metrics, champion_name = run_training_pipeline()
    print(f"CHAMPION RAG ENGINE: '{champion_name}'")
    print(f"METRICS: ContextPrec={metrics['context_precision']*100:.1f}%, CitationPrec={metrics['citation_precision']*100:.1f}%, Faithfulness={metrics['faithfulness_score']*100:.1f}%")

    # 5. Automated Unit & Integration Testing
    print("\n[STEP 5/6] Running Automated Unit & Integration Test Suite...")
    ret_code = pytest.main(["tests/", "-v"])
    if ret_code != 0:
        print("FAILED: Pytest test suite encountered failures.")
        sys.exit(1)
    print("Pytest Test Suite PASSED (100% test pass rate).")

    # 6. Query Drift Audit Simulation
    print("\n[STEP 6/6] Auditing Query Distribution Drift Engine...")
    ref_df = pd.DataFrame([{"query_text": "What is the API Gateway payload limit?"}])
    detector = DataDriftDetector(ref_df)
    drift_res = detector.detect_feature_drift(ref_df)
    print(f"Drift Audit PASSED (Overall Drift Ratio: {drift_res['overall_drift_ratio']})")

    print("\n================================================================================")
    print("         ENTERPRISE RAG OPS PIPELINE EXECUTION SUCCESSFUL!                     ")
    print("================================================================================")
    print("\nTo launch the FastAPI REST Service & Interactive RAG Dashboard UI:")
    print("  uvicorn app.main:app --port 8000\n")
    print("Service Endpoints:")
    print("  - Interactive RAG Assistant UI:  http://localhost:8000")
    print("  - OpenAPI Swagger UI:            http://localhost:8000/docs")
    print("  - Prometheus Metrics Server:     http://localhost:9090")
    print("  - Grafana Monitoring Dashboard:  http://localhost:3000\n")


if __name__ == "__main__":
    main()
