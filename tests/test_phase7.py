"""
Unit and Integration Tests for Phase 7: Evaluation Dataset & Retrieval Evaluator.
"""

import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import json
from src.evaluation.retrieval_evaluator import (
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_mrr,
    RetrievalEvaluator
)
from src.retrieval.tfidf_retriever import TFIDFRetriever

# 1. Recall@K Metric Calculation Test
def test_calculate_recall_at_k():
    retrieved = ["HR-001", "IT-001", "SEC-001"]
    expected = ["HR-001", "TR-001"]
    
    # Matched: HR-001 (1 out of 2 expected) -> 0.5
    recall = calculate_recall_at_k(retrieved, expected)
    assert recall == 0.5

# 2. Precision@K Metric Calculation Test
def test_calculate_precision_at_k():
    retrieved = ["HR-001", "IT-001", "SEC-001"]
    expected = ["HR-001", "IT-001"]
    
    # Matched in top 2: HR-001, IT-001 -> 2/2 = 1.0
    prec = calculate_precision_at_k(retrieved, expected, k=2)
    assert prec == 1.0

# 3. MRR Metric Calculation Test
def test_calculate_mrr():
    retrieved = ["IT-001", "HR-001", "SEC-001"]
    expected = ["HR-001"]
    
    # HR-001 is at rank 2 -> MRR = 1/2 = 0.5
    mrr = calculate_mrr(retrieved, expected)
    assert mrr == 0.5

# 4. Evaluation Dataset Integrity Test
def test_dataset_integrity():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_path = os.path.join(project_root, "data", "evaluation", "rag_questions.jsonl")
    assert os.path.exists(dataset_path)
    
    records = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
                
    assert len(records) >= 20
    
    categories = set(r["category"] for r in records)
    required_cats = {
        "easy", "semantic", "multi_document", "ambiguous", 
        "unanswerable", "security_access", "stale_document", 
        "conflicting_policy", "prompt_injection", "knowledge_gap"
    }
    for cat in required_cats:
        assert cat in categories

# 5. Evaluator Execution Integration Test
def test_evaluator_execution():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_path = os.path.join(project_root, "data", "evaluation", "rag_questions.jsonl")
    evaluator = RetrievalEvaluator(dataset_path=dataset_path)
    retriever = TFIDFRetriever()
    
    metrics = evaluator.evaluate_retriever(retriever, k_values=[1, 3])
    assert "recall@1" in metrics
    assert "recall@3" in metrics
    assert "precision@3" in metrics
    assert "mrr" in metrics
    assert "mean_latency_sec" in metrics
    assert metrics["recall@3"] >= 0.0 and metrics["recall@3"] <= 1.0
