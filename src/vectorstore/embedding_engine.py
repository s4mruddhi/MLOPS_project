"""
Embedding Engine Module using Sentence Transformers.
"""

import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import time
from typing import List, Union
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

class EmbeddingEngine:
    """Generates vector embeddings using SentenceTransformers with dimension validation."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        # Determine embedding dimension from sample encoding
        sample_vec = self.model.encode("test", convert_to_numpy=True)
        self.dimension = sample_vec.shape[0]

    def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self.dimension
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        if not texts:
            return []
        
        # Filter out completely empty strings safely
        processed_texts = [t if t and t.strip() else " " for t in texts]
        embeddings = self.model.encode(
            processed_texts, 
            batch_size=batch_size, 
            show_progress_bar=False, 
            convert_to_numpy=True
        )
        return embeddings.tolist()
