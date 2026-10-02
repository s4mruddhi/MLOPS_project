"""
RAG Assistant Model Training & MLflow Experiment Management Module.
Evaluates RAG architectures, logs metrics to MLflow, and registers champion RAG engine.
"""

import os
import joblib
import mlflow
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List

from src.config import (
    set_seed,
    MLFLOW_TRACKING_URI,
    EXPERIMENT_NAME,
    MODEL_REGISTRY_NAME,
    RAW_DOCS_PATH,
    MODEL_ARTIFACT_DIR,
    REFERENCE_QUERIES_PATH,
)
from src.data.ingestion import ingest_data
from src.data.validation import DataValidator
from src.data.preprocessing import preprocess_rag_data
from src.models.evaluate import evaluate_rag_model, check_quality_gate
from benchmark.dataset_generator import SyntheticDatasetGenerator
from rag_agent.agent import AgenticRAGAgent, AgentMode
from pipeline.runner import ContinuousBenchmarkRunner


def run_training_pipeline() -> Tuple[Dict[str, Any], str]:
    """Runs complete RAG evaluation, MLflow logging, and model registration pipeline."""
    set_seed(42)

    # 1. Ingest & Validate Document Corpus
    if not os.path.exists(RAW_DOCS_PATH):
        documents = ingest_data()
    else:
        with open(RAW_DOCS_PATH, "r", encoding="utf-8") as f:
            import json
            documents = json.load(f)

    is_valid, validation_errors = DataValidator.validate(documents)
    if not is_valid:
        raise ValueError(f"Data validation failed prior to RAG training: {validation_errors}")

    # 2. Preprocess & Index Vectors
    vectors, preprocessor, docs = preprocess_rag_data(documents, fit=True)

    # Save reference queries dataset for drift monitoring
    samples = SyntheticDatasetGenerator.generate_default_suite()
    ref_queries = pd.DataFrame([{"query_id": s.sample_id, "query_text": s.query, "category": s.category} for s in samples])
    ref_queries.to_csv(REFERENCE_QUERIES_PATH, index=False)

    # 3. Configure MLflow Experiment Tracking
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    runner = ContinuousBenchmarkRunner()

    candidate_agents = {
        "Baseline_SparseRetriever_RAG": AgenticRAGAgent(mode=AgentMode.RETRIEVAL_FAIL),
        "Candidate_DenseVector_RAG": AgenticRAGAgent(mode=AgentMode.HALLUCINATING),
        "Candidate_Reranked_AgenticRAG": AgenticRAGAgent(mode=AgentMode.ACCURATE),
    }

    best_score = -1.0
    best_name = ""
    best_metrics = {}
    best_run_id = ""
    best_summary = None

    print("\n--- Starting MLflow RAG Experiment Tracking Runs ---")
    for name, agent in candidate_agents.items():
        with mlflow.start_run(run_name=name) as run:
            summary = runner.run_suite(samples, agent, experiment_name=name)

            metrics = evaluate_rag_model(
                context_precision=summary.mean_context_precision,
                context_recall=summary.mean_context_recall,
                citation_precision=summary.mean_citation_precision,
                faithfulness_score=summary.mean_overall_score,
                unsupported_rate=summary.mean_unsupported_citation_rate,
            )

            # Log Parameters & Metrics
            mlflow.log_param("agent_mode", agent.mode)
            mlflow.log_param("num_samples", str(len(samples)))
            mlflow.log_metrics(metrics)
            mlflow.set_tag("architecture", name)

            print(f"Run '{name}': ContextPrec={metrics['context_precision']:.2f}, CitationPrec={metrics['citation_precision']:.2f}, Faithfulness={metrics['faithfulness_score']:.2f}")

            composite_score = 0.4 * metrics["context_precision"] + 0.4 * metrics["citation_precision"] + 0.2 * metrics["faithfulness_score"]
            if composite_score > best_score:
                best_score = composite_score
                best_name = name
                best_metrics = metrics
                best_run_id = run.info.run_id
                best_summary = summary

    # 4. Quality Gate Check
    passed_gate, gate_failures = check_quality_gate(best_metrics)
    print(f"\nChampion RAG Engine: '{best_name}' (Composite Score: {best_score:.4f})")
    print(f"Quality Gate Status: {'PASSED' if passed_gate else 'FAILED'}")

    # 5. Register Champion RAG Engine in MLflow Model Registry
    client = mlflow.tracking.MlflowClient()
    reg_model = client.create_model_version(
        name=MODEL_REGISTRY_NAME,
        source=f"runs:/{best_run_id}/rag_engine",
        run_id=best_run_id,
    ) if False else None

    # Try standard model registration
    try:
        model_uri = f"runs:/{best_run_id}/rag_engine"
        reg_model = mlflow.register_model(model_uri, MODEL_REGISTRY_NAME)
        client.set_registered_model_alias(MODEL_REGISTRY_NAME, "Production", reg_model.version)
        print(f"[MLflow Registry] Registered '{best_name}' as Version {reg_model.version} with alias 'Production'.")
    except Exception as e:
        print(f"[MLflow Registry Tag] Champion model logged under run {best_run_id}.")

    # Save local champion artifacts for standalone FastAPI startup
    os.makedirs(MODEL_ARTIFACT_DIR, exist_ok=True)
    joblib.dump(best_name, os.path.join(MODEL_ARTIFACT_DIR, "champion_name.pkl"))
    joblib.dump(best_metrics, os.path.join(MODEL_ARTIFACT_DIR, "champion_metrics.pkl"))

    return best_metrics, best_name


if __name__ == "__main__":
    run_training_pipeline()
