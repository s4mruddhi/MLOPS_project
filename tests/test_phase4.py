"""
Unit and Integration Tests for Phase 4: Document Validation, Preprocessing, and Chunking.
"""

import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import tempfile
import json
from src.data.doc_validation import DocumentValidator
from src.data.text_processor import TextCleaner, TextChunker, process_documents

@pytest.fixture
def sample_valid_doc():
    return """---
document_id: TEST-001
title: Test Document Title
department: HR
category: Leave
version: "1.0"
effective_date: "2026-01-01"
source: Test Source
access_level: employee
---

# Test Document Header

This is a paragraph inside the test document used for testing metadata extraction and chunking.

Another paragraph to ensure sufficient text length for chunking tests.
"""

@pytest.fixture
def sample_empty_doc():
    return ""

@pytest.fixture
def sample_invalid_date_doc():
    return """---
document_id: TEST-002
title: Bad Date Document
department: IT
category: VPN
version: "1.0"
effective_date: "INVALID-DATE"
source: Test Source
access_level: employee
---

Some text content here.
"""

# 1. Metadata Parsing Test
def test_metadata_parsing(sample_valid_doc):
    validator = DocumentValidator()
    metadata, body, errors = validator.parse_frontmatter(sample_valid_doc)
    assert len(errors) == 0
    assert metadata["document_id"] == "TEST-001"
    assert metadata["department"] == "HR"
    assert metadata["access_level"] == "employee"

# 2. Document Validation Test
def test_document_validation(sample_valid_doc):
    validator = DocumentValidator()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(sample_valid_doc)
        tmp_path = f.name
        
    try:
        is_valid, metadata, body, errors = validator.validate_file(tmp_path)
        assert is_valid is True
        assert len(errors) == 0
        assert metadata["document_id"] == "TEST-001"
    finally:
        os.remove(tmp_path)

# 3. Text Cleaning Test
def test_text_cleaning():
    raw_text = "Line 1  \r\n\r\n\r\n\r\nLine 2\r\n"
    cleaned = TextCleaner.clean_text(raw_text)
    assert "\r" not in cleaned
    assert "Line 1\n\nLine 2" in cleaned

# 4 & 5. Chunking & Deterministic Chunk IDs Test
def test_chunking_and_deterministic_ids():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "Word " * 100
    meta = {
        "title": "Title",
        "department": "HR",
        "category": "Leave",
        "version": "1.0",
        "effective_date": "2026-01-01",
        "source": "Source",
        "access_level": "employee"
    }
    chunks = chunker.create_chunks("TEST-001", text, meta)
    assert len(chunks) > 0
    assert chunks[0]["chunk_id"] == "TEST-001_chunk_000"
    assert chunks[1]["chunk_id"] == "TEST-001_chunk_001"

# 6. Chunk Overlap Behavior Test
def test_chunk_overlap_behavior():
    chunker = TextChunker(chunk_size=50, chunk_overlap=15)
    text = "1234567890" * 10
    meta = {"title": "T", "department": "D", "category": "C", "version": "1.0", "effective_date": "2026-01-01", "source": "S", "access_level": "employee"}
    chunks = chunker.create_chunks("TEST-001", text, meta)
    assert len(chunks) > 1
    # End of chunk 0 should overlap with start of chunk 1
    chunk0_tail = chunks[0]["text"][-10:]
    chunk1_head = chunks[1]["text"][:15]
    assert any(char in chunk1_head for char in chunk0_tail)

# 7. Metadata Preservation Test
def test_metadata_preservation(sample_valid_doc):
    validator = DocumentValidator()
    metadata, body, _ = validator.parse_frontmatter(sample_valid_doc)
    chunker = TextChunker(chunk_size=200, chunk_overlap=30)
    chunks = chunker.create_chunks("TEST-001", body, metadata)
    assert len(chunks) > 0
    c_meta = chunks[0]["metadata"]
    assert c_meta["title"] == "Test Document Title"
    assert c_meta["department"] == "HR"
    assert c_meta["access_level"] == "employee"
    assert c_meta["version"] == "1.0"
    assert c_meta["effective_date"] == "2026-01-01"

# 8. Empty Document Rejection Test
def test_empty_document_rejection():
    validator = DocumentValidator()
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("   \n  ")
        tmp_path = f.name
        
    try:
        is_valid, metadata, body, errors = validator.validate_file(tmp_path)
        assert is_valid is False
        assert any("Empty file" in e for e in errors)
    finally:
        os.remove(tmp_path)

# 9. Duplicate Document ID Detection Test
def test_duplicate_document_id_detection(sample_valid_doc):
    validator = DocumentValidator()
    with tempfile.TemporaryDirectory() as tmp_dir:
        file1 = os.path.join(tmp_dir, "doc1.txt")
        file2 = os.path.join(tmp_dir, "doc2.txt")
        with open(file1, "w", encoding="utf-8") as f:
            f.write(sample_valid_doc)
        with open(file2, "w", encoding="utf-8") as f:
            f.write(sample_valid_doc)
            
        valid_docs, rejected_docs, report = validator.validate_directory(tmp_dir)
        assert len(valid_docs) == 1
        assert len(rejected_docs) == 1
        assert any("Duplicate document_id" in e for e in rejected_docs[0]["errors"])

# 10. CHUNKING DETERMINISM TEST
def test_chunking_determinism(sample_valid_doc):
    validator = DocumentValidator()
    metadata, body, _ = validator.parse_frontmatter(sample_valid_doc)
    chunker1 = TextChunker(chunk_size=150, chunk_overlap=30)
    chunker2 = TextChunker(chunk_size=150, chunk_overlap=30)
    
    run1 = chunker1.create_chunks("TEST-001", body, metadata)
    run2 = chunker2.create_chunks("TEST-001", body, metadata)
    
    assert json.dumps(run1, sort_keys=True) == json.dumps(run2, sort_keys=True)
