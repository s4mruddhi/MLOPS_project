"""
RAG System Evaluation & Quality Gate Module.
Computes Context Precision, Context Recall, Citation Precision, and Answer Faithfulness metrics.
"""

from typing import Dict, Any, Tuple, List
from src.config import (
    MIN_CONTEXT_PRECISION,
    MIN_CITATION_PRECISION,
    MIN_FAITHFULNESS_SCORE,
)


def evaluate_rag_model(
    context_precision: float,
    context_recall: float,
    citation_precision: float,
    faithfulness_score: float,
    unsupported_rate: float,
) -> Dict[str, float]:
    """Formats RAG evaluation metrics."""
    return {
        "context_precision": round(float(context_precision), 4),
        "context_recall": round(float(context_recall), 4),
        "citation_precision": round(float(citation_precision), 4),
        "faithfulness_score": round(float(faithfulness_score), 4),
        "unsupported_citation_rate": round(float(unsupported_rate), 4),
    }


def check_quality_gate(metrics: Dict[str, float]) -> Tuple[bool, List[str]]:
    """Checks if candidate RAG system passes quality gate thresholds for production promotion."""
    failures = []

    if metrics["context_precision"] < MIN_CONTEXT_PRECISION:
        failures.append(
            f"Context Precision {metrics['context_precision']:.4f} below threshold {MIN_CONTEXT_PRECISION}"
        )

    if metrics["citation_precision"] < MIN_CITATION_PRECISION:
        failures.append(
            f"Citation Precision {metrics['citation_precision']:.4f} below threshold {MIN_CITATION_PRECISION}"
        )

    if metrics["faithfulness_score"] < MIN_FAITHFULNESS_SCORE:
        failures.append(
            f"Faithfulness Score {metrics['faithfulness_score']:.4f} below threshold {MIN_FAITHFULNESS_SCORE}"
        )

    passed = len(failures) == 0
    return passed, failures
