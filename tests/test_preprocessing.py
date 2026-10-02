"""
Unit tests for data validation and preprocessing.
"""

import pandas as pd
import numpy as np
import pytest
from src.data.ingestion import generate_enterprise_churn_dataset
from src.data.validation import DataValidator
from src.data.preprocessing import preprocess_data, FEATURE_COLUMNS


def test_data_ingestion_and_validation():
    df = generate_enterprise_churn_dataset(n_samples=100)
    assert len(df) == 100
    assert "churn" in df.columns

    is_valid, errors = DataValidator.validate(df)
    assert is_valid is True
    assert len(errors) == 0


def test_data_validation_fails_on_invalid_data():
    df = generate_enterprise_churn_dataset(n_samples=50)
    df.loc[0, "age"] = 150 # Invalid age
    is_valid, errors = DataValidator.validate(df)
    assert is_valid is False
    assert any("age" in err.lower() for err in errors)


def test_preprocessing_transform_shape_and_artifacts():
    df = generate_enterprise_churn_dataset(n_samples=200)
    X_trans, y, preprocessor, feature_names = preprocess_data(df, fit=True, save_path=None)

    assert X_trans.shape[0] == 200
    assert len(y) == 200
    assert len(feature_names) == X_trans.shape[1]
    assert not np.isnan(X_trans).any()
