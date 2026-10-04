"""
Semantic Candidate 2 Retriever Module using ChromaDB + SentenceTransformers.
"""

import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import time
from typing import List, Dict, Any
from src.retrieval.base import BaseRetriever, get_allowed_access_levels
from src.vectorstore.chroma_store import ChromaVectorStore, DEFAULT_DB_DIR, DEFAULT_COLLECTION_NAME

class SemanticRetriever(BaseRetriever):
    """Candidate 2 retrieval engine using Dense Semantic Vector Embeddings and ChromaDB persistent index."""

    def __init__(self, 
                 vector_store: ChromaVectorStore = None, 
                 db_dir: str = DEFAULT_DB_DIR,
                 collection_name: str = DEFAULT_COLLECTION_NAME):
        if vector_store:
            self.vector_store = vector_store
        else:
            self.vector_store = ChromaVectorStore(db_dir=db_dir, collection_name=collection_name)

    def retrieve(self, query_text: str, top_k: int = 5, user_role: str = "employee") -> List[Dict[str, Any]]:
        start_time = time.time()
        
        if not query_text or not query_text.strip():
            return []

        allowed_levels = get_allowed_access_levels(user_role)
        
        # Build ChromaDB metadata filter for RBAC
        if len(allowed_levels) == 1:
            where_filter = {"access_level": allowed_levels[0]}
        else:
            where_filter = {"access_level": {"$in": allowed_levels}}

        # Fetch extra results to allow post-filtering if needed
        raw_results = self.vector_store.query(
            query_text=query_text,
            n_results=top_k,
            where_filter=where_filter
        )
        
        elapsed = time.time() - start_time
        
        results = []
        for item in raw_results:
            results.append({
                "chunk_id": item["chunk_id"],
                "document_id": item["metadata"].get("document_id", ""),
                "score": item["score"],
                "text": item["text"],
                "metadata": item["metadata"],
                "latency": round(elapsed, 6)
            })
            
        return results
