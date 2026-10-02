"""
Unit & Integration Tests for Continuous RAG Evaluation Suite.
"""

import os
import pytest
from benchmark.dataset_generator import SyntheticDatasetGenerator
from rag_agent.retriever import VectorRetriever
from rag_agent.tool_executor import MockToolRegistry
from rag_agent.agent import AgenticRAGAgent, AgentMode
from eval_engine.retrieval_metrics import RetrievalEvaluator
from eval_engine.citation_verifier import CitationVerificationEngine
from eval_engine.tool_metrics import ToolExecutionEvaluator
from pipeline.runner import ContinuousBenchmarkRunner


def test_synthetic_dataset_generation_and_persistence(tmp_path):
    samples = SyntheticDatasetGenerator.generate_default_suite()
    assert len(samples) >= 5

    file_path = tmp_path / "test_benchmark.json"
    SyntheticDatasetGenerator.save_dataset(samples, str(file_path))
    assert file_path.exists()

    loaded_samples = SyntheticDatasetGenerator.load_dataset(str(file_path))
    assert len(loaded_samples) == len(samples)
    assert loaded_samples[0].sample_id == samples[0].sample_id


def test_retrieval_metrics_calculation():
    samples = SyntheticDatasetGenerator.generate_default_suite()
    sample = samples[0] # gold_context_ids: ["DOC-GATEWAY-101"]

    metrics = RetrievalEvaluator.compute_metrics(
        retrieved_chunks=sample.available_docs,
        gold_doc_ids=sample.gold_context_ids,
        k=3
    )

    assert metrics.hit_rate_k == 1.0
    assert metrics.mrr == 1.0
    assert metrics.context_recall == 1.0
    assert metrics.context_precision > 0.0


def test_citation_verifier_entailment():
    samples = SyntheticDatasetGenerator.generate_default_suite()
    sample = samples[0]
    agent = AgenticRAGAgent(mode=AgentMode.ACCURATE)

    trace = agent.execute(sample)
    verifier = CitationVerificationEngine()
    metrics, evaluated_claims = verifier.compute_citation_metrics(
        claims=trace.extracted_citations,
        retrieved_docs=trace.retrieved_chunks,
        gold_context_ids=sample.gold_context_ids,
    )

    assert metrics.citation_precision == 1.0
    assert metrics.unsupported_citation_rate == 0.0
    assert metrics.hallucination_rate == 0.0


def test_citation_verifier_hallucination_detection():
    samples = SyntheticDatasetGenerator.generate_default_suite()
    sample = samples[0]
    agent = AgenticRAGAgent(mode=AgentMode.HALLUCINATING)

    trace = agent.execute(sample)
    verifier = CitationVerificationEngine()
    metrics, evaluated_claims = verifier.compute_citation_metrics(
        claims=trace.extracted_citations,
        retrieved_docs=trace.retrieved_chunks,
        gold_context_ids=sample.gold_context_ids,
    )

    assert metrics.unsupported_citation_rate > 0.0
    assert metrics.hallucination_rate > 0.0


def test_tool_execution_metrics():
    executor = MockToolRegistry()
    trace = executor.execute_tool("get_cluster_status", {"cluster_id": "db-us-east-1"})
    assert trace.status == "success"
    assert trace.output["status"] == "HEALTHY"

    metrics = ToolExecutionEvaluator.compute_metrics(
        executed_tools=[trace],
        expected_tools=[{"tool_name": "get_cluster_status", "input_args": {"cluster_id": "db-us-east-1"}}],
    )
    assert metrics.tool_selection_accuracy == 1.0
    assert metrics.param_match_rate == 1.0
    assert metrics.tool_success_rate == 1.0


def test_continuous_benchmark_runner_and_regression_detection():
    samples = SyntheticDatasetGenerator.generate_default_suite()
    runner = ContinuousBenchmarkRunner()

    baseline_agent = AgenticRAGAgent(mode=AgentMode.ACCURATE)
    baseline_summary = runner.run_suite(samples, baseline_agent, "baseline")

    candidate_agent = AgenticRAGAgent(mode=AgentMode.HALLUCINATING)
    candidate_summary = runner.run_suite(samples, candidate_agent, "candidate")

    regression = runner.detect_regression(baseline_summary, candidate_summary)

    assert regression.is_regression is True
    assert len(regression.regression_warnings) > 0
    assert candidate_summary.hallucination_sample_count > baseline_summary.hallucination_sample_count
