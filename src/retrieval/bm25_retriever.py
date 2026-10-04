"""
BM25 Candidate 1 Retriever Module using rank-bm25.
"""

import os
import re
import json
import time
import numpy as np
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from src.retrieval.base import BaseRetriever, is_access_allowed

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_CHUNKS_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "chunks.jsonl")

def simple_tokenize(text: str) -> List[str]:
    """Simple lowercase word tokenizer."""
    return re.findall(r"\w+", text.lower())

class BM25Retriever(BaseRetriever):
    """Candidate 1 retrieval engine using BM25Okapi algorithm."""

    def __init__(self, chunks_path: str = DEFAULT_CHUNKS_PATH, chunks_list: List[Dict[str, Any]] = None):
        if chunks_list is not None:
            self.chunks = chunks_list
        elif os.path.exists(chunks_path):
            self.chunks = []
            with open(chunks_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.chunks.append(json.loads(line))
        else:
            self.chunks = []

        if self.chunks:
            corpus = [simple_tokenize(c["text"]) for c in self.chunks]
            self.bm25 = BM25Okapi(corpus)
        else:
            self.bm25 = None

    def retrieve(self, query_text: str, top_k: int = 5, user_role: str = "employee") -> List[Dict[str, Any]]:
        start_time = time.time()
        
        if not query_text or not query_text.strip() or self.bm25 is None or len(self.chunks) == 0:
            return []

        query_tokens = simple_tokenize(query_text)
        if not query_tokens:
            return []
            
        scores = self.bm25.get_scores(query_tokens)
        
        # Rank indices by BM25 score in descending order
        ranked_indices = np.argsort(scores)[::-1]
        max_score = float(np.max(scores)) if len(scores) > 0 and np.max(scores) > 0 else 1.0
        
        results = []
        for idx in ranked_indices:
            score = float(scores[idx])
            if score <= 0.0 and len(results) >= top_k:
                break
                
            chunk = self.chunks[idx]
            access_level = chunk["metadata"].get("access_level", "employee")
            
            # Access Control Filter
            if not is_access_allowed(access_level, user_role):
                continue
                
            # Normalize BM25 score relative to top score for standard scale [0, 1]
            norm_score = round(score / max_score, 4) if max_score > 0 else 0.0
            
            results.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "score": norm_score,
                "bm25_raw_score": round(score, 4),
                "text": chunk["text"],
                "metadata": chunk["metadata"]
            })
            
            if len(results) >= top_k:
                break
                
        elapsed = time.time() - start_time
        for r in results:
            r["latency"] = round(elapsed, 6)
            
        return results
