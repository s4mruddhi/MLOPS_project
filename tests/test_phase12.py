"""
Phase 12 Integration Tests for FastAPI Production Serving REST Endpoints.
"""

import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Ensure environment flags set before import
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "chroma_db_status" in data
    assert data["chunk_count"] >= 0
    assert data["document_count"] >= 0


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["application_version"] == "1.0.0"
    assert "retrieval_version" in data
    assert "prompt_version" in data
    assert "dataset_version" in data
    assert "embedding_model" in data


def test_query_endpoint_valid():
    payload = {
        "query": "What is the data retention policy for engineering logs?",
        "user_role": "employee",
        "top_k": 3,
        "retrieval_method": "semantic",
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == payload["query"]
    assert data["user_role"] == "employee"
    assert "answer" in data
    assert isinstance(data["citations"], list)
    assert isinstance(data["retrieved_documents"], list)
    assert len(data["retrieved_documents"]) <= 3
    assert data["total_latency"] >= 0.0


def test_query_endpoint_validation_error_empty():
    payload = {
        "query": "   ",
        "user_role": "employee",
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 422


def test_query_endpoint_validation_error_invalid_role():
    payload = {
        "query": "What is the policy?",
        "user_role": "invalid_super_role",
    }
    response = client.post("/query", json=payload)
    assert response.status_code == 422


def test_documents_endpoint():
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 20
    assert data["total_chunks"] >= 50
    assert isinstance(data["documents"], list)


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "ragops_http_requests_total" in response.text


def test_admin_reload_index():
    response = client.post("/admin/reload-index")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"


def test_admin_evaluate():
    response = client.post("/admin/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "details" in data
    assert "mean_groundedness_score" in data["details"]
