"""
Centralized Configuration & Reproducibility Settings for MLOps Pipeline.
"""

import os
import random
import numpy as np

# Global Reproducibility Seed
SEED = 42


def set_seed(seed: int = SEED) -> None:
    """Enforces global random seed across standard library, numpy, and ML libraries."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


# Directory Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw", "customer_churn.csv")
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed", "churn_processed.csv")
REFERENCE_DATA_PATH = os.path.join(DATA_DIR, "reference_baseline.csv")
MODEL_ARTIFACT_DIR = os.path.join(BASE_DIR, "models")

# MLflow Settings
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///" + os.path.join(BASE_DIR, "mlflow.db").replace("\\", "/"))
EXPERIMENT_NAME = "Enterprise_Customer_Churn_Prediction"
MODEL_REGISTRY_NAME = "CustomerChurnPredictor"

# Quality Gate Thresholds
MIN_ACCURACY_THRESHOLD = 0.75
MIN_F1_THRESHOLD = 0.75
MIN_ROC_AUC_THRESHOLD = 0.82
MAX_P95_LATENCY_MS = 150.0

# Ensure directories exist
os.makedirs(os.path.join(DATA_DIR, "raw"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "processed"), exist_ok=True)
os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
