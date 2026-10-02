"""
Unit tests for model training and prediction determinism.
"""

import os
import joblib
import pandas as pd
import numpy as np
import pytest
from src.data.ingestion import generate_enterprise_churn_dataset
from src.data.preprocessing import preprocess_data
from src.models.train import run_training_pipeline
from src.config import MODEL_ARTIFACT_DIR


def test_training_pipeline_execution():
    metrics, champion_name = run_training_pipeline()
    assert "f1_score" in metrics
    assert "accuracy" in metrics
    assert metrics["accuracy"] >= 0.70
    assert len(champion_name) > 0

    model_path = os.path.join(MODEL_ARTIFACT_DIR, "best_model.pkl")
    assert os.path.exists(model_path)


def test_prediction_output_bounds_and_determinism():
    df = generate_enterprise_churn_dataset(n_samples=50)
    X_trans, y, preprocessor, _ = preprocess_data(df, fit=True, save_path=None)

    model_path = os.path.join(MODEL_ARTIFACT_DIR, "best_model.pkl")
    model = joblib.load(model_path)

    probs = model.predict_proba(X_trans)[:, 1]
    preds = model.predict(X_trans)

    assert (probs >= 0.0).all() and (probs <= 1.0).all()
    assert set(preds).issubset({0, 1})
