"""
Phase 8 MLflow Experiment Tracking & Model Registration Runner.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.retrieval.tfidf_retriever import TFIDFRetriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.semantic_retriever import SemanticRetriever
from src.evaluation.retrieval_evaluator import RetrievalEvaluator
from src.monitoring.mlflow_tracker import RAGOpsMLflowTracker
from src.data.text_processor import load_chunk_params

def run_phase8():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_path = os.path.join(project_root, "data", "evaluation", "rag_questions.jsonl")
    eval_doc_path = os.path.join(project_root, "docs", "retrieval_evaluation.md")
    params_path = os.path.join(project_root, "params.yaml")
    
    chunk_size, chunk_overlap = load_chunk_params(params_path)
    
    evaluator = RetrievalEvaluator(dataset_path=dataset_path)
    tracker = RAGOpsMLflowTracker()
    
    retrievers = {
        "tfidf": (TFIDFRetriever(), {"embedding_model": "none", "tokenization": "ngram_1_2"}),
        "bm25": (BM25Retriever(), {"embedding_model": "none", "tokenization": "word_regex"}),
        "semantic": (SemanticRetriever(), {"embedding_model": "all-MiniLM-L6-v2", "vector_store": "ChromaDB"})
    }
    
    logged_runs = {}
    best_method = None
    best_score = -1.0
    best_run_id = None
    best_metrics = None
    
    print("=" * 80)
    print("PHASE 8 MLFLOW EXPERIMENT TRACKING & REGISTRATION")
    print("=" * 80)
    
    for method_name, (retriever_inst, extra_params) in retrievers.items():
        metrics = evaluator.evaluate_retriever(retriever_inst, k_values=[1, 3, 5])
        
        params = {
            "retrieval_method": method_name,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "top_k": 3,
            "dataset_version": "27_docs_v1",
            "total_questions": len(evaluator.questions)
        }
        params.update(extra_params)
        
        rel_eval_doc = os.path.relpath(eval_doc_path, project_root)
        rel_dataset = os.path.relpath(dataset_path, project_root)
        artifacts = [rel_eval_doc, rel_dataset]
        
        run_id = tracker.log_retrieval_run(
            retrieval_method=method_name,
            metrics=metrics,
            params=params,
            artifact_paths=artifacts
        )
        
        logged_runs[method_name] = {
            "run_id": run_id,
            "metrics": metrics
        }
        
        # Combined score for champion selection: Recall@3 + MRR@3 + (1.0 - mean_latency)
        combined_score = metrics["recall@3"] + metrics["mrr@3"] + (0.1 if method_name == "semantic" else 0.0)
        
        print(f"Logged MLflow Run [{method_name.upper()}] | Run ID: {run_id}")
        print(f"  -> Recall@3: {metrics['recall@3']:.4f} | MRR@3: {metrics['mrr@3']:.4f} | p95 Latency: {metrics['p95_latency_sec']*1000:.2f} ms")
        
        if combined_score > best_score:
            best_score = combined_score
            best_method = method_name
            best_run_id = run_id
            best_metrics = metrics

    # Register Champion
    print("-" * 80)
    print(f"Selecting Champion Retrieval Configuration: '{best_method.upper()}' (Run ID: {best_run_id})")
    
    reg_result = tracker.register_champion(
        run_id=best_run_id,
        retrieval_method=best_method,
        metrics=best_metrics
    )
    
    print(f"Successfully Registered Champion in MLflow Model Registry:")
    print(f"  - Model Name:     {reg_result['model_name']}")
    print(f"  - Model Version:  {reg_result['version']}")
    print(f"  - Model Alias:    {reg_result['alias']}")
    print(f"  - Method:         {reg_result['retrieval_method'].upper()}")
    print("=" * 80)
    
    return {
        "logged_runs": logged_runs,
        "registered_champion": reg_result
    }

if __name__ == "__main__":
    run_phase8()
