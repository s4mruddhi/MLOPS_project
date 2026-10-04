"""
Phase 11 Airflow DAG Task Execution Runner.
Executes all 11 RAGOps DAG tasks sequentially and reports step-by-step verification.
"""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dags.ragops_pipeline_dag import (
    task_ingest_documents,
    task_validate_documents,
    task_extract_text,
    task_clean_text,
    task_chunk_documents,
    task_generate_embeddings,
    task_update_vector_database,
    task_evaluate_retrieval,
    task_evaluate_rag,
    task_quality_gate,
    task_register_version
)

def run_phase11():
    tasks = [
        ("1. ingest_documents", task_ingest_documents),
        ("2. validate_documents", task_validate_documents),
        ("3. extract_text", task_extract_text),
        ("4. clean_text", task_clean_text),
        ("5. chunk_documents", task_chunk_documents),
        ("6. generate_embeddings", task_generate_embeddings),
        ("7. update_vector_database", task_update_vector_database),
        ("8. evaluate_retrieval", task_evaluate_retrieval),
        ("9. evaluate_rag", task_evaluate_rag),
        ("10. quality_gate", task_quality_gate),
        ("11. register_version", task_register_version)
    ]
    
    pipeline_start = time.time()
    task_results = []
    
    print("=" * 80)
    print("PHASE 11 AIRFLOW DAG PIPELINE EXECUTION REPORT")
    print("=" * 80)
    
    for task_name, task_func in tasks:
        t_start = time.time()
        try:
            task_func()
            t_elapsed = time.time() - t_start
            task_results.append((task_name, "SUCCESS", t_elapsed))
        except Exception as e:
            t_elapsed = time.time() - t_start
            task_results.append((task_name, f"FAILED: {str(e)}", t_elapsed))
            print(f"\n[X] Task '{task_name}' FAILED after {t_elapsed:.2f}s: {e}")
            raise e
            
    total_elapsed = time.time() - pipeline_start
    
    print("\n" + "=" * 80)
    print("AIRFLOW DAG TASK EXECUTION SUMMARY")
    print("=" * 80)
    print(f"{'Task Name':<28} | {'Status':<12} | {'Duration (sec)':<15}")
    print("-" * 80)
    for name, status, duration in task_results:
        print(f"{name:<28} | {status:<12} | {duration:<15.4f}")
    print("=" * 80)
    print(f"Total Pipeline Execution Time: {total_elapsed:.4f} seconds")
    print("=" * 80)
    
    return task_results

if __name__ == "__main__":
    run_phase11()
