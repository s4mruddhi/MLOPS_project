"""
Phase 15 Integration Tests: Data & Query Drift Detection Engine.
"""

import os
import sys
import pytest
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from src.monitoring.drift_detector import DataDriftDetector


@pytest.fixture
def drift_engine():
    ref_path = os.path.join(PROJECT_ROOT, "data", "evaluation", "reference_queries.csv")
    ref_df = pd.read_csv(ref_path)
    return DataDriftDetector(reference_df=ref_df)


def test_zero_drift_with_identical_queries(drift_engine):
    ref_df = drift_engine.reference_df
    res = drift_engine.detect_feature_drift(ref_df)

    assert res["drift_detected"] is False
    assert res["overall_drift_ratio"] == 0.0
    assert res["semantic_drift_score"] < 0.10


def test_in_domain_queries_low_drift(drift_engine):
    in_domain_path = os.path.join(PROJECT_ROOT, "data", "evaluation", "in_domain_current_queries.csv")
    in_domain_df = pd.read_csv(in_domain_path)
    res = drift_engine.detect_feature_drift(in_domain_df)

    assert res["drift_detected"] is False
    assert res["semantic_drift_score"] < 0.25


def test_out_of_domain_queries_high_drift(drift_engine):
    out_domain_path = os.path.join(PROJECT_ROOT, "data", "evaluation", "out_of_domain_current_queries.csv")
    out_domain_df = pd.read_csv(out_domain_path)
    res = drift_engine.detect_feature_drift(out_domain_df)

    assert res["drift_detected"] is True
    assert res["drifted_features_count"] >= 2
    assert res["semantic_drift_score"] >= 0.20


def test_empty_query_dataframe_handling(drift_engine):
    empty_df = pd.DataFrame({"query_text": []})
    res = drift_engine.detect_feature_drift(empty_df)

    assert res["drift_detected"] is False
    assert res["overall_drift_ratio"] == 0.0
