"""
Vector & Hybrid Retriever Simulator for RAG Pipeline.
"""

from typing import List, Optional
from benchmark.schema import DocumentChunk


class VectorRetriever:
    """Simulates dense vector and hybrid document retrieval with score filtering and noise injection."""

    def __init__(self, top_k: int = 3, score_threshold: float = 0.50):
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(
        self, query: str, candidate_docs: List[DocumentChunk], inject_noise: bool = False
    ) -> List[DocumentChunk]:
        """Retrieves and ranks document chunks based on score."""
        # Sort documents by relevance score descending
        sorted_docs = sorted(candidate_docs, key=lambda d: d.score, reverse=True)

        # Filter by threshold
        filtered = [d for d in sorted_docs if d.score >= self.score_threshold]

        if not filtered and sorted_docs:
            filtered = [sorted_docs[0]]  # Fallback to top-1

        results = filtered[: self.top_k]

        if inject_noise:
            # Re-order or add noise chunk to simulate retriever degradation
            results = list(reversed(results))

        return results
