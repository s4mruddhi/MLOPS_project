"""
Phase 6 Retrieval Pipeline Runner.
Evaluates and compares TF-IDF, BM25, and Semantic Retrieval.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from src.retrieval.retrieval_manager import RetrievalManager

def run_phase6():
    manager = RetrievalManager()
    
    test_queries = [
        ("What is the annual leave entitlement for employees?", "employee"),
        ("How do I report a suspicious phishing email?", "employee"),
        ("What are the break-glass access credentials for SOC?", "employee"), # RBAC test
        ("What are the break-glass access credentials for SOC?", "restricted") # RBAC test
    ]
    
    methods = ["tfidf", "bm25", "semantic"]
    
    print("=" * 80)
    print("PHASE 6 RETRIEVAL COMPARISON REPORT")
    print("=" * 80)
    
    for q_idx, (query, role) in enumerate(test_queries, 1):
        print(f"\nQuery #{q_idx}: '{query}' | User Role: '{role}'")
        print("-" * 80)
        print(f"{'Method':<12} | {'Top Chunk ID':<20} | {'Score':<8} | {'Latency (sec)':<12}")
        print("-" * 80)
        
        for m in methods:
            res = manager.retrieve(query, method=m, top_k=3, user_role=role)
            if res:
                top_item = res[0]
                chunk_id = top_item["chunk_id"]
                score = top_item["score"]
                lat = top_item["latency"]
            else:
                chunk_id = "NONE (Blocked/No Match)"
                score = 0.0
                lat = 0.0
                
            print(f"{m.upper():<12} | {chunk_id:<20} | {score:<8.4f} | {lat:<12.6f}")
            
    print("=" * 80)

if __name__ == "__main__":
    run_phase6()
