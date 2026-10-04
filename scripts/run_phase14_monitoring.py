"""
Phase 14 Verification Script: Prometheus & Grafana Monitoring & Alerting Pipeline.
"""

import os
import sys
import json
import time
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def main():
    print("==================================================")
    print("PHASE 14 — PROMETHEUS & GRAFANA MONITORING & ALERTING PIPELINE")
    print("==================================================")

    # 1. Prometheus Rule & Config Verification
    print("\n[Step 1] Inspecting Prometheus configuration & Alert Rules...")
    prom_path = os.path.join(PROJECT_ROOT, "prometheus", "prometheus.yml")
    rules_path = os.path.join(PROJECT_ROOT, "prometheus", "alert_rules.yml")

    assert os.path.exists(prom_path), "prometheus.yml missing"
    assert os.path.exists(rules_path), "alert_rules.yml missing"

    with open(rules_path, "r", encoding="utf-8") as f:
        rules_data = yaml.safe_load(f)

    configured_alerts = [r["alert"] for r in rules_data["groups"][0]["rules"]]
    print(f"Configured Prometheus Alert Rules ({len(configured_alerts)}): {configured_alerts}")

    # 2. Grafana Provisioning & Dashboard JSON Verification
    print("\n[Step 2] Inspecting Grafana Provisioning & Dashboard JSON...")
    dash_path = os.path.join(PROJECT_ROOT, "grafana", "dashboards", "ragops_dashboard.json")
    ds_path = os.path.join(PROJECT_ROOT, "grafana", "provisioning", "datasources", "prometheus.yml")

    assert os.path.exists(dash_path), "ragops_dashboard.json missing"
    assert os.path.exists(ds_path), "datasources/prometheus.yml missing"

    with open(dash_path, "r", encoding="utf-8") as f:
        dash_data = json.load(f)

    panel_titles = [p["title"] for p in dash_data["panels"]]
    print(f"Grafana Dashboard Title: '{dash_data['title']}'")
    print(f"Configured Grafana Panels ({len(panel_titles)}): {panel_titles}")

    # 3. Simulate Traffic to Populate Prometheus Metrics
    print("\n[Step 3] Simulating live RAG queries to populate metrics...")
    test_queries = [
        {"query": "What is the API Gateway payload limit?", "user_role": "employee", "retrieval_method": "semantic"},
        {"query": "What are the password requirements for IT systems?", "user_role": "employee", "retrieval_method": "tfidf"},
        {"query": "What is the remote work policy?", "user_role": "employee", "retrieval_method": "bm25"},
    ]

    for idx, q in enumerate(test_queries, 1):
        resp = client.post("/query", json=q)
        print(f"  Query {idx} ({q['retrieval_method']}): Status {resp.status_code}, Latency: {resp.json()['total_latency']}s")
        assert resp.status_code == 200

    # 4. Scrape & Validate Prometheus /metrics Endpoint Output
    print("\n[Step 4] Scraping and validating GET /metrics endpoint...")
    resp_metrics = client.get("/metrics")
    assert resp_metrics.status_code == 200
    metrics_content = resp_metrics.text

    metrics_to_check = [
        "ragops_http_requests_total",
        "ragops_query_latency_seconds_bucket",
        "ragops_query_latency_seconds_count",
        "ragops_query_latency_seconds_sum",
        "ragops_top_retrieval_score",
        "ragops_http_errors_total",
    ]

    print("Prometheus Metric Assertions:")
    for m in metrics_to_check:
        present = m in metrics_content
        print(f"  - {m}: {'FOUND [OK]' if present else 'MISSING [FAIL]'}")
        assert present, f"Metric {m} missing from /metrics endpoint output"

    print("\n==================================================")
    print("PHASE 14 MONITORING & ALERTING PIPELINE VERIFIED SUCCESSFUL!")
    print("==================================================")

if __name__ == "__main__":
    main()
