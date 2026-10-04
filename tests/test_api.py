"""
Integration tests for RAG Assistant FastAPI REST Endpoints using TestClient.
"""

import os
import pytest
from fastapi.testclient import TestClient

os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from app.main import app

client = TestClient(app)

SAMPLE_RAG_QUERY = {
    "query": "What is the maximum allowed API request payload size according to gateway docs?",
    "user_role": "employee",
    "top_k": 3,
    "retrieval_method": "semantic",
}


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "application_version" in data


def test_query_endpoint():
    response = client.post("/query", json=SAMPLE_RAG_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == SAMPLE_RAG_QUERY["query"]
    assert "answer" in data
    assert "retrieved_documents" in data


def test_documents_endpoint():
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data


def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "ragops_http_requests_total" in response.text
