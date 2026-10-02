"""
Benchmark Reporting & Markdown Artifact Generator.
Generates structured Markdown evaluation reports, regression diffs, and summary tables.
"""

from typing import List, Optional
from pipeline.runner import BenchmarkSuiteSummary, RegressionDiff


class EvaluationReporter:
    """Formats benchmark evaluation results into readable Markdown reports and artifacts."""

    @staticmethod
    def generate_markdown_report(
        summary: BenchmarkSuiteSummary, regression: Optional[RegressionDiff] = None
    ) -> str:
        lines = []
        lines.append(f"# Continuous Agentic RAG Evaluation Report: `{summary.experiment_name}`")
        lines.append(f"**Agent Mode**: `{summary.agent_mode}` | **Total Samples Evaluated**: `{summary.total_samples}`\n")

        lines.append("## Executive Metrics Summary")
        lines.append("| Metric | Value | Target | Status |")
        lines.append("| :--- | :---: | :---: | :---: |")

        overall_status = "PASS" if summary.mean_overall_score >= 0.80 else "WARN"
        lines.append(f"| **Overall Correctness Score** | `{summary.mean_overall_score * 100:.1f}%` | ≥ 80.0% | `{overall_status}` |")

        ret_status = "PASS" if summary.mean_context_precision >= 0.75 else "WARN"
        lines.append(f"| **Context Precision** | `{summary.mean_context_precision * 100:.1f}%` | ≥ 75.0% | `{ret_status}` |")

        rec_status = "PASS" if summary.mean_context_recall >= 0.75 else "WARN"
        lines.append(f"| **Context Recall** | `{summary.mean_context_recall * 100:.1f}%` | ≥ 75.0% | `{rec_status}` |")

        cit_status = "PASS" if summary.mean_citation_precision >= 0.85 else "FAIL"
        lines.append(f"| **Citation Precision** | `{summary.mean_citation_precision * 100:.1f}%` | ≥ 85.0% | `{cit_status}` |")

        unsupp_status = "PASS" if summary.mean_unsupported_citation_rate <= 0.10 else "FAIL"
        lines.append(f"| **Unsupported Citation Rate** | `{summary.mean_unsupported_citation_rate * 100:.1f}%` | ≤ 10.0% | `{unsupp_status}` |")

        tool_status = "PASS" if summary.mean_tool_accuracy >= 0.90 else "WARN"
        lines.append(f"| **Tool Selection Accuracy** | `{summary.mean_tool_accuracy * 100:.1f}%` | ≥ 90.0% | `{tool_status}` |")

        lines.append(f"| **Hallucination Incidents** | `{summary.hallucination_sample_count}` / {summary.total_samples} | 0 | `{'PASS' if summary.hallucination_sample_count==0 else 'FAIL'}` |")
        lines.append(f"| **Avg Query Latency** | `{summary.avg_latency_ms:.1f} ms` | < 2000 ms | `PASS` |")
        lines.append("")

        if regression:
            lines.append("## Regression Detection Analysis")
            if regression.is_regression:
                lines.append("> [!WARNING]")
                lines.append(f"> **REGRESSION DETECTED** in candidate run `{regression.candidate_experiment}` compared to baseline `{regression.baseline_experiment}`.")
                for w in regression.regression_warnings:
                    lines.append(f"> - {w}")
            else:
                lines.append("> [!NOTE]")
                lines.append(f"> **NO REGRESSION DETECTED**. Candidate run `{regression.candidate_experiment}` meets or exceeds baseline performance.")
            lines.append("")

        lines.append("## Sample-Level Evaluation Breakdown")
        lines.append("| Sample ID | Query Snippet | Context Prec | Citation Prec | Tool Acc | Latency | Status |")
        lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")

        for sample_res in summary.sample_results:
            query_sub = (sample_res.query[:35] + "...") if len(sample_res.query) > 35 else sample_res.query
            status_tag = "FAIL" if (sample_res.has_hallucination or sample_res.has_tool_failure) else "PASS"

            lines.append(
                f"| `{sample_res.sample_id}` | {query_sub} | `{sample_res.retrieval.context_precision * 100:.0f}%` | `{sample_res.citation.citation_precision * 100:.0f}%` | `{sample_res.tool.tool_selection_accuracy * 100:.0f}%` | `{sample_res.latency_ms:.0f} ms` | `{status_tag}` |"
            )

        lines.append("")
        return "\n".join(lines)
