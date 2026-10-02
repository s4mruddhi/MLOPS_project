"""
Unified Faithfulness & Correctness Evaluator.
Aggregates retrieval, citation, tool, and answer correctness into a single sample evaluation score.
"""

from benchmark.schema import (
    QuerySample,
    AgentTrace,
    SampleEvaluationResult,
)
from eval_engine.retrieval_metrics import RetrievalEvaluator
from eval_engine.citation_verifier import CitationVerificationEngine
from eval_engine.tool_metrics import ToolExecutionEvaluator


class SampleEvaluator:
    """Unified evaluator for an agent trace on a query sample."""

    def __init__(self):
        self.retrieval_eval = RetrievalEvaluator()
        self.citation_eval = CitationVerificationEngine()
        self.tool_eval = ToolExecutionEvaluator()

    def evaluate(self, sample: QuerySample, trace: AgentTrace) -> SampleEvaluationResult:
        # 1. Retrieval Metrics
        retrieval_metrics = self.retrieval_eval.compute_metrics(
            retrieved_chunks=trace.retrieved_chunks,
            gold_doc_ids=sample.gold_context_ids,
        )

        # 2. Citation Metrics
        citation_metrics, evaluated_claims = self.citation_eval.compute_citation_metrics(
            claims=trace.extracted_citations,
            retrieved_docs=trace.retrieved_chunks,
            gold_context_ids=sample.gold_context_ids,
        )

        # 3. Tool Metrics
        tool_metrics = self.tool_eval.compute_metrics(
            executed_tools=trace.tool_calls,
            expected_tools=sample.expected_tool_calls,
        )

        # 4. Overall Correctness Score (Weighted Composite Metric)
        # Weights: Retrieval (30%), Citation Precision (35%), Tool Accuracy (25%), Latency (<2s = 10%)
        latency_score = 1.0 if trace.total_latency_ms < 2000 else max(0.0, 1.0 - (trace.total_latency_ms - 2000) / 5000)

        overall_score = (
            0.30 * retrieval_metrics.context_precision
            + 0.35 * citation_metrics.citation_precision
            + 0.25 * tool_metrics.tool_selection_accuracy
            + 0.10 * latency_score
        )

        has_hallucination = citation_metrics.hallucination_rate > 0.0
        has_tool_failure = tool_metrics.tool_success_rate < 1.0

        return SampleEvaluationResult(
            sample_id=sample.sample_id,
            query=sample.query,
            retrieval=retrieval_metrics,
            citation=citation_metrics,
            tool=tool_metrics,
            overall_correctness_score=round(overall_score, 4),
            latency_ms=round(trace.total_latency_ms, 2),
            has_hallucination=has_hallucination,
            has_tool_failure=has_tool_failure,
        )
