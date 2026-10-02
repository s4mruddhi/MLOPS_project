"""
Integration tests for FastAPI REST Endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_CUSTOMER = {
    "customer_id": "CUST-TEST-101",
    "age": 42,
    "gender": "Female",
    "tenure": 12,
    "monthly_charges": 85.50,
    "total_charges": 1026.00,
    "contract": "Month-to-month",
    "payment_method": "Electronic check",
    "support_tickets": 3,
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
    assert "num_features" in data


def test_predict_endpoint():
    response = client.post("/predict", json=SAMPLE_CUSTOMER)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == "CUST-TEST-101"
    assert data["prediction"] in [0, 1]
    assert 0.0 <= data["churn_probability"] <= 1.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert data["latency_ms"] >= 0.0


def test_explain_endpoint():
    response = client.post("/explain", json=SAMPLE_CUSTOMER)
    assert response.status_code == 200
    data = response.json()
    assert "feature_attributions" in data
    assert len(data["feature_attributions"]) > 0


def test_drift_check_endpoint():
    batch_payload = {"customers": [SAMPLE_CUSTOMER, SAMPLE_CUSTOMER]}
    response = client.post("/drift-check", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert "drift_detected" in data
    assert "overall_drift_ratio" in data


def test_prometheus_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
