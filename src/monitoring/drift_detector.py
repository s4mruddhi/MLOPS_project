"""
Data & Prediction Drift Detection Engine.
Calculates Kolmogorov-Smirnov (KS) test and Wasserstein distance metrics between live inference batches and baseline data.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, wasserstein_distance


class DataDriftDetector:
    """Monitors feature and prediction distribution drift using statistical hypothesis testing."""

    def __init__(self, reference_df: pd.DataFrame, alpha: float = 0.05):
        self.reference_df = reference_df
        self.alpha = alpha
        self.numerical_cols = ["age", "tenure", "monthly_charges", "total_charges", "support_tickets"]

    def detect_feature_drift(self, current_df: pd.DataFrame) -> Dict[str, Any]:
        """Runs KS-2sample test across numerical features to detect feature drift."""
        drift_results = {}
        drift_count = 0

        for col in self.numerical_cols:
            if col in self.reference_df.columns and col in current_df.columns:
                ref_vals = self.reference_df[col].dropna()
                curr_vals = current_df[col].dropna()

                if len(curr_vals) < 5:
                    continue

                stat, p_value = ks_2samp(ref_vals, curr_vals)
                w_dist = wasserstein_distance(ref_vals, curr_vals)
                is_drift = bool(p_value < self.alpha)

                if is_drift:
                    drift_count += 1

                drift_results[col] = {
                    "p_value": round(float(p_value), 4),
                    "ks_statistic": round(float(stat), 4),
                    "wasserstein_distance": round(float(w_dist), 4),
                    "drift_detected": is_drift,
                }

        total_features = len(drift_results)
        drift_ratio = drift_count / max(total_features, 1)

        return {
            "drift_detected": drift_count > 0,
            "drifted_features_count": drift_count,
            "total_features": total_features,
            "overall_drift_ratio": round(drift_ratio, 4),
            "feature_details": drift_results,
        }

    @staticmethod
    def detect_prediction_drift(
        baseline_probs: np.ndarray, current_probs: np.ndarray, alpha: float = 0.05
    ) -> Dict[str, Any]:
        """Detects prediction output probability distribution drift."""
        stat, p_value = ks_2samp(baseline_probs, current_probs)
        w_dist = wasserstein_distance(baseline_probs, current_probs)
        is_drift = bool(p_value < alpha)

        return {
            "prediction_drift_detected": is_drift,
            "p_value": round(float(p_value), 4),
            "ks_statistic": round(float(stat), 4),
            "wasserstein_distance": round(float(w_dist), 4),
        }
