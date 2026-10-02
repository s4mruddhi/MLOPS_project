"""
Unit tests for document validation and RAG vector preprocessing.
"""

import pytest
from src.data.ingestion import generate_enterprise_knowledge_base
from src.data.validation import DataValidator
from src.data.preprocessing import preprocess_rag_data


def test_data_ingestion_and_validation():
    docs = generate_enterprise_knowledge_base()
    assert len(docs) >= 5
    assert "doc_id" in docs[0]

    is_valid, errors = DataValidator.validate(docs)
    assert is_valid is True
    assert len(errors) == 0


def test_document_validation_fails_on_invalid_data():
    docs = generate_enterprise_knowledge_base()
    docs[0]["text"] = "short" # Too short
    is_valid, errors = DataValidator.validate(docs)
    assert is_valid is False


def test_preprocessing_transform_shape_and_artifacts():
    docs = generate_enterprise_knowledge_base()
    vectors, preprocessor, processed_docs = preprocess_rag_data(docs, fit=True, save_path=None)

    assert vectors.shape[0] == len(docs)
    assert len(processed_docs) == len(docs)
