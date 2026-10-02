"""
Data Preprocessing & Feature Engineering Module.
Builds, fits, and applies Scikit-Learn transformers for numerical scaling and categorical encoding.
"""

import os
import joblib
import pandas as pd
import numpy as np
from typing import Tuple, Optional, List
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from src.config import MODEL_ARTIFACT_DIR, PROCESSED_DATA_PATH, set_seed

NUMERICAL_FEATURES = ["age", "tenure", "monthly_charges", "total_charges", "support_tickets"]
CATEGORICAL_FEATURES = ["gender", "contract", "payment_method"]
FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "churn"


def build_preprocessor() -> ColumnTransformer:
    """Instantiates ColumnTransformer for scaling numericals and encoding categoricals."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ]
    )
    return preprocessor


def preprocess_data(
    df: pd.DataFrame,
    preprocessor: Optional[ColumnTransformer] = None,
    fit: bool = True,
    save_path: Optional[str] = PROCESSED_DATA_PATH,
) -> Tuple[np.ndarray, Optional[np.ndarray], ColumnTransformer, List[str]]:
    """Preprocesses input dataframe and returns feature matrix X, target array y, preprocessor, and feature names."""
    set_seed(42)

    X_raw = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN].values if TARGET_COLUMN in df.columns else None

    if fit or preprocessor is None:
        preprocessor = build_preprocessor()
        X_trans = preprocessor.fit_transform(X_raw)
        # Save fitted transformer artifact
        os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
        joblib.dump(preprocessor, os.path.join(MODEL_ARTIFACT_DIR, "preprocessor.pkl"))
    else:
        X_trans = preprocessor.transform(X_raw)

    # Get feature names after one-hot encoding
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_feature_names = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
    feature_names = NUMERICAL_FEATURES + cat_feature_names

    if save_path and y is not None:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        processed_df = pd.DataFrame(X_trans, columns=feature_names)
        processed_df["churn"] = y
        processed_df.to_csv(save_path, index=False)
        print(f"[Preprocessing] Saved processed dataset to '{save_path}'.")

    return X_trans, y, preprocessor, feature_names
