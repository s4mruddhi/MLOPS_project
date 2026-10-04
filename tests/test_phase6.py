"""
Unit and Integration Tests for Phase 6: Retrieval System (TF-IDF, BM25, Semantic).
"""

import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import tempfile
import json
from src.retrieval.tfidf_retriever import TFIDFRetriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.semantic_retriever import SemanticRetriever
from src.retrieval.retrieval_manager import RetrievalManager

@pytest.fixture
def sample_chunks():
    return [
        {
            "chunk_id": "HR-001_chunk_000",
            "document_id": "HR-001",
            "chunk_index": 0,
            "text": "Full-time employees are entitled to 24 days of annual leave per calendar year.",
            "metadata": {
                "title": "Annual Leave Policy",
                "department": "HR",
                "category": "Leave",
                "version": "1.0",
                "effective_date": "2026-01-01",
                "source": "Internal HR Policy",
                "access_level": "employee"
            }
        },
        {
            "chunk_id": "IT-001_chunk_000",
            "document_id": "IT-001",
            "chunk_index": 0,
            "text": "Employees must use their organization issued account to authenticate to the corporate VPN with MFA.",
            "metadata": {
                "title": "VPN Access Guide",
                "department": "IT",
                "category": "VPN",
                "version": "1.0",
                "effective_date": "2026-01-15",
                "source": "IT Knowledge Base",
                "access_level": "employee"
            }
        },
        {
            "chunk_id": "SEC-005_chunk_000",
            "document_id": "SEC-005",
            "chunk_index": 0,
            "text": "Break glass emergency access procedure for SOC personnel stored in HSM vault.",
            "metadata": {
                "title": "Security Operations Access Procedure",
                "department": "Cybersecurity",
                "category": "Access Control",
                "version": "1.0",
                "effective_date": "2026-01-01",
                "source": "Internal SOC Manual",
                "access_level": "restricted"
            }
        }
    ]

# 1. TF-IDF Retriever Test
def test_tfidf_retriever(sample_chunks):
    retriever = TFIDFRetriever(chunks_list=sample_chunks)
    res = retriever.retrieve("annual leave days", top_k=2, user_role="employee")
    assert len(res) > 0
    assert res[0]["chunk_id"] == "HR-001_chunk_000"
    assert "score" in res[0]
    assert "latency" in res[0]
    assert res[0]["score"] > 0

# 2. BM25 Retriever Test
def test_bm25_retriever(sample_chunks):
    retriever = BM25Retriever(chunks_list=sample_chunks)
    res = retriever.retrieve("corporate VPN MFA", top_k=2, user_role="employee")
    assert len(res) > 0
    assert res[0]["chunk_id"] == "IT-001_chunk_000"
    assert "score" in res[0]
    assert "latency" in res[0]
    assert res[0]["score"] > 0

# 3. Semantic Retriever Test
def test_semantic_retriever():
    retriever = SemanticRetriever()
    res = retriever.retrieve("annual leave entitlement", top_k=2, user_role="employee")
    assert len(res) > 0
    assert "chunk_id" in res[0]
    assert "score" in res[0]
    assert "latency" in res[0]

# 4. Access Control (RBAC) Enforcement Test
def test_access_control_enforcement(sample_chunks):
    tfidf = TFIDFRetriever(chunks_list=sample_chunks)
    bm25 = BM25Retriever(chunks_list=sample_chunks)
    
    # Employee query for restricted text
    emp_res_tfidf = tfidf.retrieve("Break glass emergency HSM vault", top_k=5, user_role="employee")
    emp_res_bm25 = bm25.retrieve("Break glass emergency HSM vault", top_k=5, user_role="employee")
    
    # Should NOT return SEC-005_chunk_000 for employee role
    assert not any(r["chunk_id"] == "SEC-005_chunk_000" for r in emp_res_tfidf)
    assert not any(r["chunk_id"] == "SEC-005_chunk_000" for r in emp_res_bm25)
    
    # Restricted query for restricted text
    rest_res_tfidf = tfidf.retrieve("Break glass emergency HSM vault", top_k=5, user_role="restricted")
    rest_res_bm25 = bm25.retrieve("Break glass emergency HSM vault", top_k=5, user_role="restricted")
    
    # SHOULD return SEC-005_chunk_000 for restricted role
    assert any(r["chunk_id"] == "SEC-005_chunk_000" for r in rest_res_tfidf)
    assert any(r["chunk_id"] == "SEC-005_chunk_000" for r in rest_res_bm25)

# 5. Top_k Parameter Behavior Test
def test_top_k_parameter():
    manager = RetrievalManager()
    for method in ["tfidf", "bm25", "semantic"]:
        res_k1 = manager.retrieve("policy", method=method, top_k=1, user_role="employee")
        res_k3 = manager.retrieve("policy", method=method, top_k=3, user_role="employee")
        assert len(res_k1) <= 1
        assert len(res_k3) <= 3
