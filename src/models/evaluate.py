"""
Model Evaluation & Quality Gate Module.
Computes classification metrics, ROC-AUC, confusion matrix, and checks quality gate thresholds.
"""

from typing import Dict, Any, Tuple, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from src.config import MIN_ACCURACY_THRESHOLD, MIN_F1_THRESHOLD, MIN_ROC_AUC_THRESHOLD


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
    """Computes comprehensive classification metrics."""
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob)

    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
    }


def check_quality_gate(metrics: Dict[str, float]) -> Tuple[bool, List[str]]:
    """Checks if model metrics pass minimum enterprise quality gate thresholds for production release."""
    failures = []

    if metrics["accuracy"] < MIN_ACCURACY_THRESHOLD:
        failures.append(
            f"Accuracy {metrics['accuracy']:.4f} is below minimum threshold {MIN_ACCURACY_THRESHOLD}"
        )

    if metrics["f1_score"] < MIN_F1_THRESHOLD:
        failures.append(
            f"F1-Score {metrics['f1_score']:.4f} is below minimum threshold {MIN_F1_THRESHOLD}"
        )

    if metrics["roc_auc"] < MIN_ROC_AUC_THRESHOLD:
        failures.append(
            f"ROC-AUC {metrics['roc_auc']:.4f} is below minimum threshold {MIN_ROC_AUC_THRESHOLD}"
        )

    passed = len(failures) == 0
    return passed, failures
