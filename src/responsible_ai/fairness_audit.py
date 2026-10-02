"""
Bias & Demographic Fairness Auditor.
Evaluates Demographic Parity, Disparate Impact, and Equal Opportunity across demographic subgroups.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class FairnessAuditor:
    """Audits model predictions for demographic bias and algorithmic fairness."""

    @staticmethod
    def audit_fairness(
        df: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray, sensitive_attribute: str = "gender"
    ) -> Dict[str, Any]:
        """Calculates Demographic Parity Ratio, Disparate Impact, and Equal Opportunity Difference."""
        subgroups = df[sensitive_attribute].unique()

        selection_rates = {}
        tpr_rates = {}

        for group in subgroups:
            mask = (df[sensitive_attribute] == group).values
            group_pred = y_pred[mask]
            group_true = y_true[mask]

            # Selection Rate = P(pred = 1)
            sel_rate = np.mean(group_pred) if len(group_pred) > 0 else 0.0
            selection_rates[group] = float(sel_rate)

            # True Positive Rate = P(pred = 1 | true = 1)
            positives = (group_true == 1)
            tpr = np.mean(group_pred[positives]) if np.sum(positives) > 0 else 0.0
            tpr_rates[group] = float(tpr)

        # Calculate Disparate Impact (Ratio of lowest selection rate to highest selection rate)
        max_rate = max(selection_rates.values())
        min_rate = min(selection_rates.values())
        disparate_impact = min_rate / max_rate if max_rate > 0 else 1.0

        # Equal Opportunity Difference (Max TPR - Min TPR)
        max_tpr = max(tpr_rates.values())
        min_tpr = min(tpr_rates.values())
        eq_opportunity_diff = max_tpr - min_tpr

        # 80% Rule Check (Four-Fifths Rule for EEOC Compliance)
        passes_80_rule = bool(disparate_impact >= 0.80)

        return {
            "sensitive_attribute": sensitive_attribute,
            "selection_rates_by_group": selection_rates,
            "tpr_rates_by_group": tpr_rates,
            "disparate_impact_ratio": round(float(disparate_impact), 4),
            "equal_opportunity_difference": round(float(eq_opportunity_diff), 4),
            "passes_four_fifths_rule": passes_80_rule,
        }
