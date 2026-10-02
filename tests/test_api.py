"""
Integration tests for RAG Assistant FastAPI REST Endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_RAG_QUERY = {
    "query": "What is the maximum allowed API request payload size according to gateway docs?",
    "top_k": 3,
    "include_citations": True,
}


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


def test_model_info_endpoint():
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "num_documents" in data


def test_ask_endpoint():
    response = client.post("/ask", json=SAMPLE_RAG_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == SAMPLE_RAG_QUERY["query"]
    assert len(data["generated_answer"]) > 0
    assert len(data["retrieved_sources"]) > 0
    assert data["latency_ms"] >= 0.0


def test_explain_endpoint():
    response = client.post("/explain", json=SAMPLE_RAG_QUERY)
    assert response.status_code == 200
    data = response.json()
    assert "citation_precision" in data
    assert "claim_attributions" in data


def test_drift_check_endpoint():
    batch_payload = {"queries": [SAMPLE_RAG_QUERY, SAMPLE_RAG_QUERY]}
    response = client.post("/drift-check", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert "drift_detected" in data
    assert "overall_drift_ratio" in data


def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "rag_http_requests_total" in response.text
