"""
Centralized Configuration & Reproducibility Settings for Enterprise RAG Ops Pipeline.
"""

import os
import random
import numpy as np

# Global Reproducibility Seed
SEED = 42


def set_seed(seed: int = SEED) -> None:
    """Enforces global random seed across Python, NumPy, and ML libraries."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


# Directory Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DOCS_PATH = os.path.join(DATA_DIR, "raw", "knowledge_docs.json")
PROCESSED_CHUNKS_PATH = os.path.join(DATA_DIR, "processed", "rag_chunks.csv")
REFERENCE_QUERIES_PATH = os.path.join(DATA_DIR, "reference_queries.csv")
MODEL_ARTIFACT_DIR = os.path.join(BASE_DIR, "models")

# MLflow Settings
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///" + os.path.join(BASE_DIR, "mlflow.db").replace("\\", "/"))
EXPERIMENT_NAME = "Enterprise_Knowledge_Assistant_RAG_Ops"
MODEL_REGISTRY_NAME = "EnterpriseRAGAssistant"

# RAG Quality Gate Thresholds
MIN_CONTEXT_PRECISION = 0.75
MIN_CITATION_PRECISION = 0.80
MIN_FAITHFULNESS_SCORE = 0.80
MAX_P95_LATENCY_MS = 150.0

# Ensure directories exist
os.makedirs(os.path.join(DATA_DIR, "raw"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "processed"), exist_ok=True)
os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
