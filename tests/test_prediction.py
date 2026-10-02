"""
Unit tests for RAG Assistant execution and quality gate evaluation.
"""

import os
import joblib
import pytest
from src.data.ingestion import generate_enterprise_knowledge_base
from src.data.preprocessing import preprocess_rag_data
from src.models.train import run_training_pipeline
from src.config import MODEL_ARTIFACT_DIR


def test_training_pipeline_execution():
    metrics, champion_name = run_training_pipeline()
    assert "context_precision" in metrics
    assert "citation_precision" in metrics
    assert metrics["context_precision"] >= 0.75
    assert len(champion_name) > 0

    champion_file = os.path.join(MODEL_ARTIFACT_DIR, "champion_name.pkl")
    assert os.path.exists(champion_file)


def test_rag_vector_transformation():
    docs = generate_enterprise_knowledge_base()
    vectors, preprocessor, _ = preprocess_rag_data(docs, fit=True, save_path=None)

    query_vec = preprocessor.transform_query("What is the API Gateway payload limit?")
    assert query_vec.shape[1] == vectors.shape[1]
