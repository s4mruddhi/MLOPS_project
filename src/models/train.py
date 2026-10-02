"""
Model Training & MLflow Experiment Management Module.
Trains Baseline and Candidate models, logs artifacts to MLflow, and registers champion model.
"""

import os
import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from src.config import (
    set_seed,
    MLFLOW_TRACKING_URI,
    EXPERIMENT_NAME,
    MODEL_REGISTRY_NAME,
    RAW_DATA_PATH,
    MODEL_ARTIFACT_DIR,
    REFERENCE_DATA_PATH,
)
from src.data.ingestion import ingest_data
from src.data.validation import DataValidator
from src.data.preprocessing import preprocess_data
from src.models.evaluate import evaluate_model, check_quality_gate


def run_training_pipeline() -> Tuple[Dict[str, Any], str]:
    """Runs complete training, evaluation, MLflow logging, and model registration pipeline."""
    set_seed(42)

    # 1. Ingest & Validate Data
    if not os.path.exists(RAW_DATA_PATH):
        df_raw = ingest_data()
    else:
        df_raw = pd.read_csv(RAW_DATA_PATH)

    is_valid, validation_errors = DataValidator.validate(df_raw)
    if not is_valid:
        raise ValueError(f"Data validation failed prior to training: {validation_errors}")

    # Save reference baseline for drift monitoring
    df_raw.to_csv(REFERENCE_DATA_PATH, index=False)

    # 2. Preprocess Data
    X_trans, y, preprocessor, feature_names = preprocess_data(df_raw, fit=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X_trans, y, test_size=0.20, random_state=42, stratify=y
    )

    # 3. Configure MLflow Experiment Tracking
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    models_to_train = {
        "Baseline_LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "Candidate_RandomForest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "Candidate_GradientBoosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42),
    }

    best_score = -1.0
    best_model_name = ""
    best_model_obj = None
    best_metrics = {}
    best_run_id = ""

    print("\n--- Starting MLflow Experiment Tracking Runs ---")
    for name, model in models_to_train.items():
        with mlflow.start_run(run_name=name) as run:
            # Train Model
            model.fit(X_train, y_train)

            # Predict & Evaluate
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]
            metrics = evaluate_model(y_test, y_pred, y_prob)

            # Log Parameters & Metrics
            mlflow.log_params(model.get_params())
            mlflow.log_metrics(metrics)
            mlflow.set_tag("model_type", name)
            mlflow.set_tag("dataset_samples", str(len(df_raw)))

            # Log Sklearn Model Artifact
            mlflow.sklearn.log_model(model, artifact_path="model")

            print(f"Run '{name}': F1={metrics['f1_score']:.4f}, ROC-AUC={metrics['roc_auc']:.4f}, Acc={metrics['accuracy']:.4f}")

            # Track Best Champion Model based on ROC-AUC + F1
            composite_score = 0.5 * metrics["f1_score"] + 0.5 * metrics["roc_auc"]
            if composite_score > best_score:
                best_score = composite_score
                best_model_name = name
                best_model_obj = model
                best_metrics = metrics
                best_run_id = run.info.run_id

    # 4. Quality Gate Check
    passed_gate, gate_failures = check_quality_gate(best_metrics)
    print(f"\nChampion Model: '{best_model_name}' (Composite Score: {best_score:.4f})")
    print(f"Quality Gate Status: {'PASSED' if passed_gate else 'FAILED'}")

    if not passed_gate:
        print(f"[WARNING] Champion model failed quality gate: {gate_failures}")

    # 5. Register Best Model in MLflow Model Registry
    model_uri = f"runs:/{best_run_id}/model"
    reg_model = mlflow.register_model(model_uri, MODEL_REGISTRY_NAME)

    # Set metadata tags and production alias
    client = mlflow.tracking.MlflowClient()
    client.set_registered_model_tag(MODEL_REGISTRY_NAME, "task", "customer_churn_classification")
    client.set_registered_model_tag(MODEL_REGISTRY_NAME, "framework", "scikit-learn")
    client.set_model_version_tag(MODEL_REGISTRY_NAME, reg_model.version, "quality_gate_passed", str(passed_gate))
    client.set_registered_model_alias(MODEL_REGISTRY_NAME, "Production", reg_model.version)

    print(f"[MLflow Registry] Registered '{best_model_name}' as Version {reg_model.version} with alias 'Production'.")

    # Save local best model pkl for standalone FastAPI deployment fallback
    os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
    joblib.dump(best_model_obj, os.path.join(MODEL_ARTIFACT_DIR, "best_model.pkl"))
    joblib.dump(feature_names, os.path.join(MODEL_ARTIFACT_DIR, "feature_names.pkl"))
    print(f"[Artifacts] Saved best model to '{os.path.join(MODEL_ARTIFACT_DIR, 'best_model.pkl')}'.")

    return best_metrics, best_model_name


if __name__ == "__main__":
    run_training_pipeline()
