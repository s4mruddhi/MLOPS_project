"""
Query & Data Drift Detection Engine for RAG Assistant.
Calculates Kolmogorov-Smirnov (KS-test), Wasserstein distance, Vocabulary Jaccard Distance, and Semantic Embedding Cosine Shift.
"""

import os
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from scipy.stats import ks_2samp, wasserstein_distance
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class DataDriftDetector:
    """Monitors incoming query distribution drift against reference baseline queries."""

    def __init__(self, reference_df: pd.DataFrame, alpha: float = 0.05, drift_threshold: float = 0.75):
        self.reference_df = reference_df
        self.alpha = alpha
        self.drift_threshold = drift_threshold
        self.embedder = SentenceTransformer(DEFAULT_EMBEDDING_MODEL)

        self.ref_queries = (
            self.reference_df["query_text"].astype(str).tolist()
            if "query_text" in self.reference_df.columns
            else []
        )
        self.ref_word_counts = (
            np.array([len(q.split()) for q in self.ref_queries])
            if self.ref_queries
            else np.array([5])
        )
        self.ref_char_counts = (
            np.array([len(q) for q in self.ref_queries])
            if self.ref_queries
            else np.array([30])
        )
        self.ref_embeddings = (
            self.embedder.encode(self.ref_queries, show_progress_bar=False)
            if self.ref_queries
            else np.zeros((1, 384))
        )

    def detect_feature_drift(self, current_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates statistical drift for query length, character counts, vocabulary, and semantic embeddings."""
        current_queries = (
            current_df["query_text"].astype(str).tolist()
            if "query_text" in current_df.columns
            else []
        )
        if not current_queries:
            return {
                "drift_detected": False,
                "drifted_features_count": 0,
                "total_features": 4,
                "overall_drift_ratio": 0.0,
                "semantic_drift_score": 0.0,
                "feature_details": {},
            }

        curr_word_counts = np.array([len(q.split()) for q in current_queries])
        curr_char_counts = np.array([len(q) for q in current_queries])
        curr_embeddings = self.embedder.encode(current_queries, show_progress_bar=False)

        drift_count = 0
        feature_details = {}

        # 1. Word Count Distribution Drift (KS-test & Wasserstein)
        ks_words_stat, ks_words_p = ks_2samp(self.ref_word_counts, curr_word_counts)
        w_dist_words = wasserstein_distance(self.ref_word_counts, curr_word_counts)
        is_word_drift = bool(ks_words_p < self.alpha)
        if is_word_drift:
            drift_count += 1

        feature_details["word_count_distribution"] = {
            "p_value": round(float(ks_words_p), 4),
            "ks_statistic": round(float(ks_words_stat), 4),
            "wasserstein_distance": round(float(w_dist_words), 4),
            "drift_detected": is_word_drift,
        }

        # 2. Character Count Distribution Drift
        ks_chars_stat, ks_chars_p = ks_2samp(self.ref_char_counts, curr_char_counts)
        w_dist_chars = wasserstein_distance(self.ref_char_counts, curr_char_counts)
        is_char_drift = bool(ks_chars_p < self.alpha)
        if is_char_drift:
            drift_count += 1

        feature_details["char_count_distribution"] = {
            "p_value": round(float(ks_chars_p), 4),
            "ks_statistic": round(float(ks_chars_stat), 4),
            "wasserstein_distance": round(float(w_dist_chars), 4),
            "drift_detected": is_char_drift,
        }

        # 3. Vocabulary Overlap / Jaccard Distance
        ref_words_set = set(" ".join(self.ref_queries).lower().split())
        curr_words_set = set(" ".join(current_queries).lower().split())
        intersection = len(ref_words_set & curr_words_set)
        union = len(ref_words_set | curr_words_set) if (ref_words_set | curr_words_set) else 1
        jaccard_similarity = intersection / union
        jaccard_distance = round(1.0 - jaccard_similarity, 4)
        is_vocab_drift = bool(jaccard_distance > 0.80)
        if is_vocab_drift:
            drift_count += 1

        feature_details["vocabulary_drift"] = {
            "jaccard_similarity": round(float(jaccard_similarity), 4),
            "jaccard_distance": jaccard_distance,
            "drift_detected": is_vocab_drift,
        }

        # 4. Semantic Embedding Centroid Cosine Shift
        ref_centroid = np.mean(self.ref_embeddings, axis=0)
        curr_centroid = np.mean(curr_embeddings, axis=0)

        ref_norm = np.linalg.norm(ref_centroid)
        curr_norm = np.linalg.norm(curr_centroid)

        if ref_norm > 0 and curr_norm > 0:
            cosine_sim = np.dot(ref_centroid, curr_centroid) / (ref_norm * curr_norm)
            cosine_dist = round(float(1.0 - cosine_sim), 4)
        else:
            cosine_dist = 0.0

        is_semantic_drift = bool(cosine_dist > 0.25)
        if is_semantic_drift:
            drift_count += 1

        feature_details["semantic_embedding_drift"] = {
            "cosine_distance": cosine_dist,
            "drift_detected": is_semantic_drift,
        }

        total_features = 4
        overall_drift_ratio = round(drift_count / total_features, 4)
        overall_drift_detected = bool(is_semantic_drift or overall_drift_ratio >= self.drift_threshold)

        return {
            "drift_detected": overall_drift_detected,
            "drifted_features_count": drift_count,
            "total_features": total_features,
            "overall_drift_ratio": overall_drift_ratio,
            "semantic_drift_score": cosine_dist,
            "feature_details": feature_details,
        }
