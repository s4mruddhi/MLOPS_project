"""
Continuous Evaluation Benchmark Runner & Regression Detector.
Runs dataset suites through RAG agent, collects evaluation metrics, and detects regressions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from benchmark.schema import QuerySample, SampleEvaluationResult
from rag_agent.agent import AgenticRAGAgent
from eval_engine.faithfulness import SampleEvaluator


@dataclass
class BenchmarkSuiteSummary:
    experiment_name: str
    agent_mode: str
    total_samples: int
    mean_overall_score: float
    mean_context_precision: float
    mean_context_recall: float
    mean_citation_precision: float
    mean_unsupported_citation_rate: float
    mean_tool_accuracy: float
    hallucination_sample_count: int
    tool_failure_sample_count: int
    avg_latency_ms: float
    sample_results: List[SampleEvaluationResult] = field(default_factory=list)


@dataclass
class RegressionDiff:
    baseline_experiment: str
    candidate_experiment: str
    score_delta: float
    precision_delta: float
    citation_precision_delta: float
    hallucination_delta: int
    is_regression: bool
    regression_warnings: List[str]


class ContinuousBenchmarkRunner:
    """Executes evaluation benchmarks and compares candidate runs against baselines."""

    def __init__(self):
        self.evaluator = SampleEvaluator()

    def run_suite(
        self,
        samples: List[QuerySample],
        agent: AgenticRAGAgent,
        experiment_name: str = "BenchmarkRun",
    ) -> BenchmarkSuiteSummary:
        results: List[SampleEvaluationResult] = []

        for sample in samples:
            # 1. Execute agent
            trace = agent.execute(sample)

            # 2. Evaluate trace
            result = self.evaluator.evaluate(sample, trace)
            results.append(result)

        total = len(results)
        if total == 0:
            return BenchmarkSuiteSummary(
                experiment_name=experiment_name,
                agent_mode=agent.mode,
                total_samples=0,
                mean_overall_score=0.0,
                mean_context_precision=0.0,
                mean_context_recall=0.0,
                mean_citation_precision=0.0,
                mean_unsupported_citation_rate=0.0,
                mean_tool_accuracy=0.0,
                hallucination_sample_count=0,
                tool_failure_sample_count=0,
                avg_latency_ms=0.0,
                sample_results=[],
            )

        mean_overall = sum(r.overall_correctness_score for r in results) / total
        mean_ctx_prec = sum(r.retrieval.context_precision for r in results) / total
        mean_ctx_rec = sum(r.retrieval.context_recall for r in results) / total
        mean_cit_prec = sum(r.citation.citation_precision for r in results) / total
        mean_unsupported = sum(r.citation.unsupported_citation_rate for r in results) / total
        mean_tool_acc = sum(r.tool.tool_selection_accuracy for r in results) / total
        hallucination_count = sum(1 for r in results if r.has_hallucination)
        tool_fail_count = sum(1 for r in results if r.has_tool_failure)
        avg_latency = sum(r.latency_ms for r in results) / total

        return BenchmarkSuiteSummary(
            experiment_name=experiment_name,
            agent_mode=agent.mode,
            total_samples=total,
            mean_overall_score=round(mean_overall, 4),
            mean_context_precision=round(mean_ctx_prec, 4),
            mean_context_recall=round(mean_ctx_rec, 4),
            mean_citation_precision=round(mean_cit_prec, 4),
            mean_unsupported_citation_rate=round(mean_unsupported, 4),
            mean_tool_accuracy=round(mean_tool_acc, 4),
            hallucination_sample_count=hallucination_count,
            tool_failure_sample_count=tool_fail_count,
            avg_latency_ms=round(avg_latency, 2),
            sample_results=results,
        )

    @staticmethod
    def detect_regression(
        baseline: BenchmarkSuiteSummary, candidate: BenchmarkSuiteSummary, threshold: float = 0.05
    ) -> RegressionDiff:
        """Compares a candidate experiment run against a baseline to detect regressions."""
        score_delta = candidate.mean_overall_score - baseline.mean_overall_score
        precision_delta = candidate.mean_context_precision - baseline.mean_context_precision
        cit_delta = candidate.mean_citation_precision - baseline.mean_citation_precision
        hallucination_delta = candidate.hallucination_sample_count - baseline.hallucination_sample_count

        warnings = []
        is_regression = False

        if score_delta < -threshold:
            is_regression = True
            warnings.append(
                f"Overall Score dropped by {abs(score_delta):.2%} (from {baseline.mean_overall_score} to {candidate.mean_overall_score})"
            )

        if cit_delta < -threshold:
            is_regression = True
            warnings.append(
                f"Citation Precision dropped by {abs(cit_delta):.2%} (from {baseline.mean_citation_precision} to {candidate.mean_citation_precision})"
            )

        if hallucination_delta > 0:
            is_regression = True
            warnings.append(
                f"Hallucination count increased by +{hallucination_delta} samples (from {baseline.hallucination_sample_count} to {candidate.hallucination_sample_count})"
            )

        return RegressionDiff(
            baseline_experiment=baseline.experiment_name,
            candidate_experiment=candidate.experiment_name,
            score_delta=round(score_delta, 4),
            precision_delta=round(precision_delta, 4),
            citation_precision_delta=round(cit_delta, 4),
            hallucination_delta=hallucination_delta,
            is_regression=is_regression,
            regression_warnings=warnings,
        )
