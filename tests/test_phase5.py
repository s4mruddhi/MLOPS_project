"""
Unit and Integration Tests for Phase 5: ChromaDB & Embedding Engine.
"""

import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import tempfile
import json
from src.vectorstore.embedding_engine import EmbeddingEngine
from src.vectorstore.chroma_store import ChromaVectorStore

@pytest.fixture
def sample_chunk_records():
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
            "chunk_id": "SEC-005_chunk_000",
            "document_id": "SEC-005",
            "chunk_index": 0,
            "text": "Break-glass administrative accounts for core domain controllers are stored in the HSM vault.",
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

# 1. Embedding Generation Test
def test_embedding_generation():
    engine = EmbeddingEngine()
    vec = engine.embed_text("Test sentence for embedding.")
    assert isinstance(vec, list)
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)

# 2. Vector Dimensions Test
def test_vector_dimensions():
    engine = EmbeddingEngine()
    assert engine.dimension == 384
    vecs = engine.embed_documents(["Sentence 1", "Sentence 2"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 384
    assert len(vecs[1]) == 384

# 3 & 4. Index Creation & Metadata Preservation Test
def test_index_creation_and_metadata_preservation(sample_chunk_records):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        store = ChromaVectorStore(db_dir=tmp_dir, collection_name="test_col")
        result = store.add_chunks(sample_chunk_records)
        assert result["added_count"] == 2
        assert store.count() == 2
        
        # Query HR-001 chunk
        res = store.query("annual leave entitlement", n_results=1)
        assert len(res) == 1
        assert res[0]["chunk_id"] == "HR-001_chunk_000"
        meta = res[0]["metadata"]
        assert meta["title"] == "Annual Leave Policy"
        assert meta["department"] == "HR"
        assert meta["access_level"] == "employee"
        assert meta["version"] == "1.0"

# 5. Index Reload Test
def test_index_reload(sample_chunk_records):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        store = ChromaVectorStore(db_dir=tmp_dir, collection_name="test_col")
        store.add_chunks(sample_chunk_records)
        assert store.count() == 2
        
        # Create a new instance pointing to same directory (reloads from disk)
        reloaded_store = ChromaVectorStore(db_dir=tmp_dir, collection_name="test_col")
        assert reloaded_store.count() == 2
        res = reloaded_store.query("annual leave", n_results=1)
        assert len(res) == 1
        assert res[0]["chunk_id"] == "HR-001_chunk_000"

# 6. Empty Input Handling Test
def test_empty_input_handling():
    engine = EmbeddingEngine()
    empty_vec = engine.embed_text("")
    assert len(empty_vec) == 384
    assert empty_vec == [0.0] * 384
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        store = ChromaVectorStore(db_dir=tmp_dir, collection_name="test_col")
        empty_res = store.query("")
        assert len(empty_res) == 0

# 7. Metadata Filtering (Access Control) Test
def test_access_control_filtering(sample_chunk_records):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        store = ChromaVectorStore(db_dir=tmp_dir, collection_name="test_col")
        store.add_chunks(sample_chunk_records)
        
        # Query with filter for employee access level only
        employee_results = store.query(
            "security operations HSM break-glass", 
            n_results=5, 
            where_filter={"access_level": "employee"}
        )
        # Should not return SEC-005 (which has access_level: restricted)
        assert len(employee_results) == 1
        assert employee_results[0]["chunk_id"] != "SEC-005_chunk_000"
