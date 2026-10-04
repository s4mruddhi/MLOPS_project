"""
TF-IDF Baseline Retriever Module.
"""

import os
import json
import time
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.retrieval.base import BaseRetriever, is_access_allowed

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_CHUNKS_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "chunks.jsonl")

class TFIDFRetriever(BaseRetriever):
    """Baseline retrieval engine using Scikit-Learn TF-IDF vectorizer and Cosine Similarity."""

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

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None)
        if self.chunks:
            texts = [c["text"] for c in self.chunks]
            self.matrix = self.vectorizer.fit_transform(texts)
        else:
            self.matrix = None

    def retrieve(self, query_text: str, top_k: int = 5, user_role: str = "employee") -> List[Dict[str, Any]]:
        start_time = time.time()
        
        if not query_text or not query_text.strip() or self.matrix is None or len(self.chunks) == 0:
            return []

        query_vec = self.vectorizer.transform([query_text])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        
        # Rank indices by similarity score in descending order
        ranked_indices = np.argsort(scores)[::-1]
        
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
                
            results.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "score": round(score, 4),
                "text": chunk["text"],
                "metadata": chunk["metadata"]
            })
            
            if len(results) >= top_k:
                break
                
        elapsed = time.time() - start_time
        for r in results:
            r["latency"] = round(elapsed, 6)
            
        return results
