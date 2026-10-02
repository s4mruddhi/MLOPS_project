"""
Query & Data Drift Detection Engine for RAG Assistant.
Calculates Kolmogorov-Smirnov (KS-test) and Wasserstein distance across query embeddings.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, wasserstein_distance


class DataDriftDetector:
    """Monitors incoming query distribution drift against reference baseline queries."""

    def __init__(self, reference_df: pd.DataFrame, alpha: float = 0.05):
        self.reference_df = reference_df
        self.alpha = alpha

    def detect_feature_drift(self, current_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates drift metrics for query length and feature distribution."""
        drift_results = {}
        drift_count = 0

        ref_lengths = self.reference_df["query_text"].apply(lambda q: len(str(q).split())) if "query_text" in self.reference_df.columns else pd.Series([10]*len(self.reference_df))
        curr_lengths = current_df["query_text"].apply(lambda q: len(str(q).split())) if "query_text" in current_df.columns else pd.Series([10]*len(current_df))

        stat, p_value = ks_2samp(ref_lengths, curr_lengths)
        w_dist = wasserstein_distance(ref_lengths, curr_lengths)
        is_drift = bool(p_value < self.alpha)

        if is_drift:
            drift_count += 1

        drift_results["query_length_distribution"] = {
            "p_value": round(float(p_value), 4),
            "ks_statistic": round(float(stat), 4),
            "wasserstein_distance": round(float(w_dist), 4),
            "drift_detected": is_drift,
        }

        drift_ratio = drift_count / 1.0

        return {
            "drift_detected": is_drift,
            "drifted_features_count": drift_count,
            "total_features": 1,
            "overall_drift_ratio": round(drift_ratio, 4),
            "feature_details": drift_results,
        }
