"""
Unified Retrieval Manager supporting TF-IDF, BM25, and Semantic Retrieval.
"""

from typing import List, Dict, Any
from src.retrieval.base import BaseRetriever
from src.retrieval.tfidf_retriever import TFIDFRetriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.semantic_retriever import SemanticRetriever

class RetrievalManager:
    """Factory and Dispatcher for all RAG retrieval strategies."""

    def __init__(self, chunks_path: str = None, db_dir: str = None):
        self.tfidf_retriever = TFIDFRetriever(chunks_path=chunks_path) if chunks_path else TFIDFRetriever()
        self.bm25_retriever = BM25Retriever(chunks_path=chunks_path) if chunks_path else BM25Retriever()
        self.semantic_retriever = SemanticRetriever(db_dir=db_dir) if db_dir else SemanticRetriever()

    def get_retriever(self, method: str) -> BaseRetriever:
        method_lower = method.lower().strip()
        if method_lower == "tfidf":
            return self.tfidf_retriever
        elif method_lower == "bm25":
            return self.bm25_retriever
        elif method_lower in ["semantic", "vector"]:
            return self.semantic_retriever
        else:
            raise ValueError(f"Unknown retrieval method '{method}'. Supported: 'tfidf', 'bm25', 'semantic'.")

    def retrieve(self, query_text: str, method: str = "semantic", top_k: int = 5, user_role: str = "employee") -> List[Dict[str, Any]]:
        retriever = self.get_retriever(method)
        return retriever.retrieve(query_text=query_text, top_k=top_k, user_role=user_role)
