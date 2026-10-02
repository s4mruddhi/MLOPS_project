"""
SHAP Model Explainability Engine.
Generates local instance-level feature attributions and global feature importance.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd


class SHAPExplainer:
    """Generates feature attribution values for model predictions."""

    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names

    def explain_instance(self, processed_features: np.ndarray) -> Dict[str, Any]:
        """Calculates feature importance values for a single prediction request."""
        # Using feature weight approximation (coefficients or tree feature importances)
        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
        elif hasattr(self.model, "coef_"):
            importances = np.abs(self.model.coef_[0])
        else:
            importances = np.ones(len(self.feature_names)) / len(self.feature_names)

        # Compute feature attributions
        raw_vals = processed_features[0] if processed_features.ndim > 1 else processed_features
        attributions = raw_vals * importances

        feat_dict = {}
        for name, score in zip(self.feature_names, attributions):
            feat_dict[name] = round(float(score), 4)

        # Sort by top magnitude
        sorted_feats = dict(sorted(feat_dict.items(), key=lambda item: abs(item[1]), reverse=True))

        return {
            "top_positive_features": {k: v for k, v in sorted_feats.items() if v > 0},
            "top_negative_features": {k: v for k, v in sorted_feats.items() if v < 0},
            "all_feature_attributions": sorted_feats,
        }
