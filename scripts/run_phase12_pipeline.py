"""
Phase 12 Verification Script: FastAPI Production Serving & Endpoint Validation.
"""

import os
import sys
import json
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Ensure environment flags set
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from fastapi.testclient import TestClient
from app.main import app

def main():
    print("==================================================")
    print("PHASE 12 — FASTAPI PRODUCTION SERVING & API PIPELINE")
    print("==================================================")

    client = TestClient(app)

    # 1. Health Probe Verification
    print("\n[Step 1] Verifying GET /health endpoint...")
    resp_health = client.get("/health")
    print(f"Status Code: {resp_health.status_code}")
    print(f"Response: {json.dumps(resp_health.json(), indent=2)}")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "HEALTHY"

    # 2. Version Information Verification
    print("\n[Step 2] Verifying GET /version endpoint...")
    resp_version = client.get("/version")
    print(f"Status Code: {resp_version.status_code}")
    print(f"Response: {json.dumps(resp_version.json(), indent=2)}")
    assert resp_version.status_code == 200
    assert resp_version.json()["application_version"] == "1.0.0"

    # 3. Query RAG Assistant Verification
    print("\n[Step 3] Verifying POST /query endpoint...")
    query_payload = {
        "query": "What is the maximum allowed API request payload size?",
        "user_role": "employee",
        "top_k": 3,
        "retrieval_method": "semantic"
    }
    resp_query = client.post("/query", json=query_payload)
    print(f"Status Code: {resp_query.status_code}")
    query_data = resp_query.json()
    print(f"Query: {query_data['query']}")
    print(f"Generated Answer: {query_data['answer']}")
    print(f"Citations: {query_data['citations']}")
    print(f"Retrieved Docs Count: {len(query_data['retrieved_documents'])}")
    print(f"Total Latency: {query_data['total_latency']}s")
    assert resp_query.status_code == 200
    assert len(query_data["answer"]) > 0

    # 4. Input Validation Error Handling Verification
    print("\n[Step 4] Verifying input validation error handling (empty query & invalid role)...")
    bad_payload_1 = {"query": "   ", "user_role": "employee"}
    resp_bad_1 = client.post("/query", json=bad_payload_1)
    print(f"Empty Query Status Code (Expected 422): {resp_bad_1.status_code}")
    assert resp_bad_1.status_code == 422

    bad_payload_2 = {"query": "Valid query", "user_role": "super_hacker"}
    resp_bad_2 = client.post("/query", json=bad_payload_2)
    print(f"Invalid Role Status Code (Expected 422): {resp_bad_2.status_code}")
    assert resp_bad_2.status_code == 422

    # 5. Document Summary Verification
    print("\n[Step 5] Verifying GET /documents endpoint...")
    resp_docs = client.get("/documents")
    print(f"Status Code: {resp_docs.status_code}")
    docs_data = resp_docs.json()
    print(f"Total Documents: {docs_data['total_documents']}")
    print(f"Total Chunks: {docs_data['total_chunks']}")
    assert resp_docs.status_code == 200
    assert docs_data["total_documents"] >= 20

    # 6. Prometheus Metrics Scraper Verification
    print("\n[Step 6] Verifying GET /metrics endpoint...")
    resp_metrics = client.get("/metrics")
    print(f"Status Code: {resp_metrics.status_code}")
    print(f"Metrics Output Snippet:\n{resp_metrics.text[:300]}...")
    assert resp_metrics.status_code == 200
    assert "ragops_http_requests_total" in resp_metrics.text

    # 7. Admin Action Endpoints Verification
    print("\n[Step 7] Verifying POST /admin/reload-index endpoint...")
    resp_reload = client.post("/admin/reload-index")
    print(f"Status Code: {resp_reload.status_code}")
    print(f"Response: {json.dumps(resp_reload.json(), indent=2)}")
    assert resp_reload.status_code == 200

    print("\n[Step 8] Verifying POST /admin/evaluate endpoint...")
    resp_eval = client.post("/admin/evaluate")
    print(f"Status Code: {resp_eval.status_code}")
    print(f"Response: {json.dumps(resp_eval.json(), indent=2)}")
    assert resp_eval.status_code == 200

    print("\n==================================================")
    print("PHASE 12 FASTAPI PIPELINE VERIFICATION SUCCESSFUL!")
    print("==================================================")

if __name__ == "__main__":
    main()
