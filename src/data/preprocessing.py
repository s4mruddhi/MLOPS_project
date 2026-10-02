"""
Document Chunking & Vector Preprocessing Pipeline for RAG.
Transforms raw knowledge documents into chunk embeddings and vector search indexes.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from src.config import MODEL_ARTIFACT_DIR, PROCESSED_CHUNKS_PATH, set_seed


class RAGVectorPreprocessor:
    """Chunks documents and generates vector embedding matrices for semantic search."""

    def __init__(self, max_features: int = 500):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
        self.document_chunks: List[Dict[str, Any]] = []

    def fit_transform(self, documents: List[Dict[str, Any]]) -> np.ndarray:
        """Processes document corpus into searchable chunk vectors."""
        self.document_chunks = documents
        texts = [doc["text"] for doc in documents]
        vectors = self.vectorizer.fit_transform(texts).toarray()
        return vectors

    def transform_query(self, query: str) -> np.ndarray:
        """Transforms a user query into vector space."""
        return self.vectorizer.transform([query]).toarray()


def preprocess_rag_data(
    documents: List[Dict[str, Any]],
    preprocessor: Optional[RAGVectorPreprocessor] = None,
    fit: bool = True,
    save_path: Optional[str] = PROCESSED_CHUNKS_PATH,
) -> Tuple[np.ndarray, RAGVectorPreprocessor, List[Dict[str, Any]]]:
    """Preprocesses enterprise document corpus into indexed vector representations."""
    set_seed(42)

    if fit or preprocessor is None:
        preprocessor = RAGVectorPreprocessor()
        vectors = preprocessor.fit_transform(documents)

        # Save artifacts
        os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
        joblib.dump(preprocessor, os.path.join(MODEL_ARTIFACT_DIR, "rag_preprocessor.pkl"))
        joblib.dump(vectors, os.path.join(MODEL_ARTIFACT_DIR, "vector_index.pkl"))
        joblib.dump(documents, os.path.join(MODEL_ARTIFACT_DIR, "raw_documents.pkl"))
    else:
        texts = [doc["text"] for doc in documents]
        vectors = preprocessor.vectorizer.transform(texts).toarray()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df_chunks = pd.DataFrame(documents)
        df_chunks.to_csv(save_path, index=False)
        print(f"[Preprocessing] Saved processed RAG chunks to '{save_path}'.")

    return vectors, preprocessor, documents
