"""
Phase 14 Integration Tests: Prometheus & Grafana Monitoring & Alerting Validation.
"""

import os
import sys
import json
import yaml
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_prometheus_alert_rules_exist_and_valid():
    rules_path = os.path.join(PROJECT_ROOT, "prometheus", "alert_rules.yml")
    assert os.path.exists(rules_path), "prometheus/alert_rules.yml must exist"

    with open(rules_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "groups" in data
    alert_names = [r["alert"] for r in data["groups"][0]["rules"]]
    assert "HighQueryLatency" in alert_names
    assert "HighErrorRate" in alert_names
    assert "LowRetrievalScore" in alert_names


def test_prometheus_config_includes_rules():
    prom_path = os.path.join(PROJECT_ROOT, "prometheus", "prometheus.yml")
    assert os.path.exists(prom_path), "prometheus/prometheus.yml must exist"

    with open(prom_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "rule_files" in data
    assert "alert_rules.yml" in data["rule_files"]


def test_grafana_dashboard_json_valid():
    dash_path = os.path.join(PROJECT_ROOT, "grafana", "dashboards", "ragops_dashboard.json")
    assert os.path.exists(dash_path), "grafana/dashboards/ragops_dashboard.json must exist"

    with open(dash_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "panels" in data
    assert len(data["panels"]) >= 4
    titles = [p["title"] for p in data["panels"]]
    assert any("Total RAG HTTP Requests" in t for t in titles)
    assert any("Query Latency" in t for t in titles)


def test_grafana_provisioning_valid():
    ds_path = os.path.join(PROJECT_ROOT, "grafana", "provisioning", "datasources", "prometheus.yml")
    provider_path = os.path.join(PROJECT_ROOT, "grafana", "provisioning", "dashboards", "dashboards.yml")

    assert os.path.exists(ds_path), "grafana/provisioning/datasources/prometheus.yml must exist"
    assert os.path.exists(provider_path), "grafana/provisioning/dashboards/dashboards.yml must exist"

    with open(ds_path, "r", encoding="utf-8") as f:
        ds_data = yaml.safe_load(f)
    assert ds_data["datasources"][0]["name"] == "Prometheus"

    with open(provider_path, "r", encoding="utf-8") as f:
        provider_data = yaml.safe_load(f)
    assert len(provider_data["providers"]) > 0


def test_fastapi_metrics_endpoint_scraping():
    # Make a query request to update metrics
    payload = {
        "query": "What is the security access level for HR documents?",
        "user_role": "employee",
        "top_k": 3,
        "retrieval_method": "semantic"
    }
    resp_query = client.post("/query", json=payload)
    assert resp_query.status_code == 200

    # Scrape metrics
    resp_metrics = client.get("/metrics")
    assert resp_metrics.status_code == 200
    metrics_text = resp_metrics.text

    assert "ragops_http_requests_total" in metrics_text
    assert "ragops_query_latency_seconds" in metrics_text
    assert "ragops_top_retrieval_score" in metrics_text
