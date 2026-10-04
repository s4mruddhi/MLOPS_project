"""
Unit and Integration Tests for Phase 8: MLflow Tracking & Model Registry.
"""

import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import tempfile
import mlflow
from src.monitoring.mlflow_tracker import RAGOpsMLflowTracker

@pytest.fixture
def temp_mlflow_tracker():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        db_path = os.path.join(tmp_dir, "test_mlflow.db")
        tracking_uri = f"sqlite:///{db_path}"
        tracker = RAGOpsMLflowTracker(tracking_uri=tracking_uri, experiment_name="Test_RAGOps_Exp")
        yield tracker

# 1. MLflow Experiment Initialization Test
def test_mlflow_experiment_initialization(temp_mlflow_tracker):
    assert temp_mlflow_tracker.experiment_id is not None
    exp = mlflow.get_experiment(temp_mlflow_tracker.experiment_id)
    assert exp.name == "Test_RAGOps_Exp"

# 2. Logging Retrieval Run Test
def test_logging_retrieval_run(temp_mlflow_tracker):
    metrics = {"recall@3": 0.95, "precision@3": 0.80, "mrr": 0.95, "mean_latency_sec": 0.045}
    params = {"chunk_size": 400, "chunk_overlap": 80, "embedding_model": "all-MiniLM-L6-v2"}
    
    run_id = temp_mlflow_tracker.log_retrieval_run("semantic", metrics=metrics, params=params)
    assert run_id is not None
    
    run_data = temp_mlflow_tracker.client.get_run(run_id)
    assert run_data.data.params["retrieval_method"] == "semantic"
    assert float(run_data.data.metrics["recall_at_3"]) == 0.95
    assert int(run_data.data.params["chunk_size"]) == 400

# 3. Model Registration & Champion Alias Test
def test_model_registration_and_alias(temp_mlflow_tracker):
    metrics = {"recall@3": 0.95, "mrr": 0.95}
    params = {"chunk_size": 400}
    
    run_id = temp_mlflow_tracker.log_retrieval_run("semantic", metrics=metrics, params=params)
    
    reg_info = temp_mlflow_tracker.register_champion(
        run_id=run_id,
        retrieval_method="semantic",
        metrics=metrics,
        model_name="Test_RAGOps_Champion"
    )
    
    assert reg_info["model_name"] == "Test_RAGOps_Champion"
    assert reg_info["version"] is not None
    assert reg_info["alias"] == "champion"
    
    # Verify alias resolution via MLflow client
    alias_mv = temp_mlflow_tracker.client.get_model_version_by_alias("Test_RAGOps_Champion", "champion")
    assert alias_mv.run_id == run_id
