"""
Retrieval Metrics & Benchmark Evaluator Engine.
Calculates Recall@K, Precision@K, MRR, Context Relevance, and Latency.
"""

import os
import time
import json
import numpy as np
from typing import List, Dict, Any
from src.retrieval.base import BaseRetriever

def calculate_recall_at_k(retrieved_doc_ids: List[str], expected_doc_ids: List[str]) -> float:
    if not expected_doc_ids:
        return 1.0
    matched = set(retrieved_doc_ids) & set(expected_doc_ids)
    return float(len(matched) / len(set(expected_doc_ids)))

def calculate_precision_at_k(retrieved_doc_ids: List[str], expected_doc_ids: List[str], k: int) -> float:
    if k <= 0:
        return 0.0
    if not expected_doc_ids:
        return 1.0 if len(retrieved_doc_ids) == 0 else 0.0
    matched = [d for d in retrieved_doc_ids[:k] if d in set(expected_doc_ids)]
    return float(len(matched) / k)

def calculate_mrr(retrieved_doc_ids: List[str], expected_doc_ids: List[str]) -> float:
    if not expected_doc_ids:
        return 1.0
    for rank, doc_id in enumerate(retrieved_doc_ids, start=1):
        if doc_id in expected_doc_ids:
            return float(1.0 / rank)
    return 0.0

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "evaluation", "rag_questions.jsonl")

class RetrievalEvaluator:
    """Evaluates retrieval engines against golden benchmark dataset."""

    def __init__(self, dataset_path: str = DEFAULT_DATASET_PATH):
        self.dataset_path = dataset_path
        self.questions = []
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.questions.append(json.loads(line))

    def evaluate_retriever(self, retriever: BaseRetriever, k_values: List[int] = [1, 3, 5]) -> Dict[str, Any]:
        results_by_k = {k: {"recall": [], "precision": [], "mrr": []} for k in k_values}
        latencies = []
        context_relevance_scores = []
        
        category_breakdown = {}
        
        for q in self.questions:
            query = q["question"]
            expected_docs = q.get("expected_document_ids", [])
            role = q.get("required_access_level", "employee")
            answerable = q.get("answerable", True)
            cat = q.get("category", "general")
            
            max_k = max(k_values)
            start_time = time.time()
            retrieved_items = retriever.retrieve(query, top_k=max_k, user_role=role)
            elapsed = time.time() - start_time
            latencies.append(elapsed)
            
            retrieved_doc_ids = [item["document_id"] for item in retrieved_items]
            scores = [item["score"] for item in retrieved_items]
            avg_score = float(np.mean(scores)) if scores else 0.0
            context_relevance_scores.append(avg_score)
            
            if cat not in category_breakdown:
                category_breakdown[cat] = {"count": 0, "recall_at_3": [], "mrr": []}
            category_breakdown[cat]["count"] += 1
            
            # Skip unanswerable for recall calculation if expected_docs is empty
            if answerable and expected_docs:
                rec_at_3 = calculate_recall_at_k(retrieved_doc_ids[:3], expected_docs)
                mrr_val = calculate_mrr(retrieved_doc_ids[:3], expected_docs)
                category_breakdown[cat]["recall_at_3"].append(rec_at_3)
                category_breakdown[cat]["mrr"].append(mrr_val)

                for k in k_values:
                    sub_ids = retrieved_doc_ids[:k]
                    rec = calculate_recall_at_k(sub_ids, expected_docs)
                    prec = calculate_precision_at_k(sub_ids, expected_docs, k)
                    mrr = calculate_mrr(sub_ids, expected_docs)
                    
                    results_by_k[k]["recall"].append(rec)
                    results_by_k[k]["precision"].append(prec)
                    results_by_k[k]["mrr"].append(mrr)

        metrics = {}
        for k in k_values:
            metrics[f"recall@{k}"] = round(float(np.mean(results_by_k[k]["recall"])), 4) if results_by_k[k]["recall"] else 0.0
            metrics[f"precision@{k}"] = round(float(np.mean(results_by_k[k]["precision"])), 4) if results_by_k[k]["precision"] else 0.0
            metrics[f"mrr@{k}"] = round(float(np.mean(results_by_k[k]["mrr"])), 4) if results_by_k[k]["mrr"] else 0.0

        metrics["mrr"] = metrics.get(f"mrr@{max(k_values)}", 0.0)
        metrics["mean_latency_sec"] = round(float(np.mean(latencies)), 6)
        metrics["p95_latency_sec"] = round(float(np.percentile(latencies, 95)), 6)
        metrics["mean_context_relevance"] = round(float(np.mean(context_relevance_scores)), 4)
        
        # Format category breakdown summary
        cat_summary = {}
        for cat, data in category_breakdown.items():
            cat_summary[cat] = {
                "count": data["count"],
                "mean_recall_at_3": round(float(np.mean(data["recall_at_3"])), 4) if data["recall_at_3"] else 1.0,
                "mean_mrr": round(float(np.mean(data["mrr"])), 4) if data["mrr"] else 1.0
            }
        metrics["category_breakdown"] = cat_summary
        
        return metrics
