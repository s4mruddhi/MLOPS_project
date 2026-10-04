"""
Unit and Integration Tests for Phase 10: Groundedness & Failure Attribution Evaluator.
"""

import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.evaluation.rag_evaluator import (
    calculate_groundedness,
    calculate_answer_relevance,
    RAGEvaluator
)
from src.generation.llm_client import FALLBACK_MESSAGE
from src.generation.rag_generator import RAGGenerator

# 1. Groundedness Calculation Test
def test_calculate_groundedness():
    chunks = [
        {"text": "Full-time employees are entitled to 24 days of annual leave per calendar year.", "score": 0.8}
    ]
    supported_ans = "Full-time employees are entitled to 24 days of annual leave. [HR-001_chunk_000]"
    unsupported_ans = "Employees get 50 days of leave and unlimited free gold coins."
    
    score_supported = calculate_groundedness(supported_ans, chunks)
    score_unsupported = calculate_groundedness(unsupported_ans, chunks)
    
    assert score_supported >= 0.8
    assert score_unsupported <= 0.3

# 2. Answer Relevance Calculation Test
def test_calculate_answer_relevance():
    ref = "Employees get 24 days of annual leave per year."
    ans = "Full-time employees get 24 days of annual leave."
    
    relevance = calculate_answer_relevance(ans, ref, "annual leave days")
    assert relevance >= 0.6

# 3. Fallback Groundedness Test
def test_fallback_groundedness():
    fallback_score = calculate_groundedness(FALLBACK_MESSAGE, [])
    assert fallback_score == 1.0

# 4. Failure Attribution Classifier Logic Test
def test_failure_attribution_classifier():
    evaluator = RAGEvaluator()
    
    # Test Knowledge Gap
    q_unanswerable = {"expected_document_ids": [], "answerable": False}
    resp_fallback = {"answer": FALLBACK_MESSAGE, "citations": [], "retrieved_documents": []}
    assert evaluator.classify_failure(q_unanswerable, resp_fallback) == "KNOWLEDGE_GAP"
    
    # Test Retrieval Failure
    q_hr = {"expected_document_ids": ["HR-001"], "answerable": True}
    resp_missed = {"answer": "Some text", "citations": ["IT-001_chunk_000"], "retrieved_documents": [{"document_id": "IT-001", "score": 0.8}]}
    assert evaluator.classify_failure(q_hr, resp_missed) == "RETRIEVAL_FAILURE"

# 5. Full RAG Evaluator Integration Test
def test_full_rag_evaluator_integration():
    generator = RAGGenerator()
    evaluator = RAGEvaluator()
    
    metrics = evaluator.evaluate_rag_pipeline(generator)
    assert "mean_groundedness_score" in metrics
    assert "mean_answer_relevance" in metrics
    assert "citation_correctness_rate" in metrics
    assert "failure_attribution" in metrics
    assert metrics["total_questions_evaluated"] == 20
    assert metrics["mean_groundedness_score"] >= 0.70
