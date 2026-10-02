"""
Unit tests for Responsible AI & Bias/Fairness Audits.
"""

import pandas as pd
import numpy as np
import pytest
from src.responsible_ai.fairness_audit import FairnessAuditor


def test_fairness_audit_calculation():
    df = pd.DataFrame({
        "gender": ["Male", "Male", "Male", "Male", "Female", "Female", "Female", "Female"],
    })
    y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
    y_pred = np.array([1, 1, 1, 0, 1, 0, 0, 0]) # Male selection rate: 3/4=0.75, Female selection rate: 1/4=0.25

    audit = FairnessAuditor.audit_fairness(df, y_true, y_pred, sensitive_attribute="gender")

    assert audit["sensitive_attribute"] == "gender"
    assert audit["disparate_impact_ratio"] < 1.0
    assert "passes_four_fifths_rule" in audit
