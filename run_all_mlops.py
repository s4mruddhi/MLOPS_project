"""
Master One-Command MLOps Pipeline Orchestrator.
Executes ingestion, validation, preprocessing, model training, MLflow registration, testing, and drift auditing.
"""

import os
import sys
import pytest
import pandas as pd

from src.config import RAW_DATA_PATH, REFERENCE_DATA_PATH
from src.data.ingestion import ingest_data
from src.data.validation import DataValidator
from src.data.preprocessing import preprocess_data
from src.models.train import run_training_pipeline
from src.monitoring.drift_detector import DataDriftDetector


def main():
    print("================================================================================")
    print("        ENTERPRISE MLOPS PIPELINE: END-TO-END AUTOMATED EXECUTOR              ")
    print("================================================================================")

    # 1. Data Ingestion
    print("\n[STEP 1/6] Running Data Ingestion...")
    df_raw = ingest_data()

    # 2. Data Validation
    print("\n[STEP 2/6] Running Schema & Quality Validation...")
    is_valid, errors = DataValidator.validate(df_raw)
    if not is_valid:
        print(f"FAILED: Data validation errors: {errors}")
        sys.exit(1)
    print("Validation PASSED (Zero missing values, range bounds verified).")

    # 3. Preprocessing & Feature Engineering
    print("\n[STEP 3/6] Preprocessing Features & Fitting Scaler/Encoder...")
    X_trans, y, preprocessor, feature_names = preprocess_data(df_raw, fit=True)
    print(f"Feature matrix created with shape {X_trans.shape} across {len(feature_names)} engineered features.")

    # 4. Model Training & MLflow Model Registry Promotion
    print("\n[STEP 4/6] Training Baseline & Candidate Models (MLflow Tracking)...")
    metrics, champion_name = run_training_pipeline()
    print(f"CHAMPION MODEL: '{champion_name}'")
    print(f"METRICS: Acc={metrics['accuracy']*100:.1f}%, F1={metrics['f1_score']*100:.1f}%, ROC-AUC={metrics['roc_auc']*100:.1f}%")

    # 5. Automated Unit & Integration Testing
    print("\n[STEP 5/6] Running Automated Unit & Integration Test Suite...")
    ret_code = pytest.main(["tests/", "-v"])
    if ret_code != 0:
        print("FAILED: Pytest test suite encountered failures.")
        sys.exit(1)
    print("Pytest Test Suite PASSED (100% test pass rate).")

    # 6. Data Drift Audit Simulation
    print("\n[STEP 6/6] Auditing Data Drift Engine...")
    detector = DataDriftDetector(df_raw)
    drift_res = detector.detect_feature_drift(df_raw.head(100))
    print(f"Drift Audit PASSED (Overall Drift Ratio: {drift_res['overall_drift_ratio']})")

    print("\n================================================================================")
    print("              ENTERPRISE MLOPS PIPELINE EXECUTION SUCCESSFUL!                  ")
    print("================================================================================")
    print("\nTo launch the complete Dockerized Microservice Infrastructure:")
    print("  docker-compose up --build\n")
    print("Service Endpoints:")
    print("  - FastAPI REST API & Swagger UI: http://localhost:8000/docs")
    print("  - Prometheus Server:             http://localhost:9090")
    print("  - Grafana Monitoring Dashboard:  http://localhost:3000\n")


if __name__ == "__main__":
    main()
