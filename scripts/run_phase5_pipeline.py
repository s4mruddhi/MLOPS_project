"""
Phase 5 ChromaDB Indexing Pipeline Runner.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from src.vectorstore.chroma_store import ChromaVectorStore

def run_phase5():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    chunks_jsonl_path = os.path.join(project_root, "data", "processed", "chunks.jsonl")
    
    if not os.path.exists(chunks_jsonl_path):
        raise FileNotFoundError(f"Chunks file not found at {chunks_jsonl_path}. Run Phase 4 pipeline first.")
        
    chunk_records = []
    with open(chunks_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunk_records.append(json.loads(line))
                
    vector_store = ChromaVectorStore()
    vector_store.reset_collection()
    
    index_result = vector_store.add_chunks(chunk_records)
    
    # Run test query
    sample_query = "What is the annual leave entitlement for employees?"
    query_results = vector_store.query(sample_query, n_results=3)
    
    print("=" * 60)
    print("PHASE 5 CHROMADB INDEXING REPORT")
    print("=" * 60)
    print(f"Chunks Input Count:           {len(chunk_records)}")
    print(f"Chunks Indexed in ChromaDB:   {index_result['added_count']}")
    print(f"Total Items in Collection:    {index_result['total_items_in_collection']}")
    print(f"Indexing Execution Time:      {index_result['indexing_time']:.4f} seconds")
    print(f"Embedding Vector Dimensions:  {vector_store.embedding_engine.dimension}")
    print(f"Embedding Model:              {vector_store.embedding_engine.model_name}")
    print("=" * 60)
    print(f"Sample Query: '{sample_query}'")
    print(f"Retrieved Top Match: [{query_results[0]['chunk_id']}] Score: {query_results[0]['score']}")
    print("=" * 60)
    
    return index_result

if __name__ == "__main__":
    run_phase5()
