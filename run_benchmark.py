"""
CLI Entry Point for Continuous RAG Evaluation & Regression Testing.
Runs baseline and candidate experiments across synthetic/real enterprise RAG benchmarks.
"""

import os
import argparse
from benchmark.dataset_generator import SyntheticDatasetGenerator
from rag_agent.agent import AgenticRAGAgent, AgentMode
from pipeline.runner import ContinuousBenchmarkRunner
from pipeline.reporter import EvaluationReporter


def main():
    parser = argparse.ArgumentParser(description="Continuous Agentic RAG Benchmark & Regression Evaluator")
    parser.add_argument("--dataset-out", type=str, default="data/synthetic_benchmark.json", help="Path to save benchmark dataset")
    parser.add_argument("--report-out", type=str, default="evaluation_report.md", help="Path to save markdown report")
    args = parser.parse_args()

    # Ensure data directory exists
    os.makedirs(os.path.dirname(args.dataset_out), exist_ok=True)

    print("================================================================================")
    print("      CONTINUOUS AGENTIC RAG EVALUATION & REGRESSION BENCHMARK SUITE          ")
    print("================================================================================")

    # 1. Generate / Load Synthetic Enterprise Benchmark Dataset
    print(f"\n[1/4] Generating Enterprise Synthetic Benchmark Suite...")
    samples = SyntheticDatasetGenerator.generate_default_suite()
    SyntheticDatasetGenerator.save_dataset(samples, args.dataset_out)
    print(f"      Saved {len(samples)} benchmark query samples to '{args.dataset_out}'")

    # 2. Initialize Runner
    runner = ContinuousBenchmarkRunner()

    # 3. Run Baseline Run (Accurate Production Agent)
    print("\n[2/4] Running Baseline Experiment: 'v1.0-accurate-production'...")
    baseline_agent = AgenticRAGAgent(mode=AgentMode.ACCURATE)
    baseline_summary = runner.run_suite(
        samples=samples,
        agent=baseline_agent,
        experiment_name="v1.0-baseline-accurate",
    )
    print(f"      Baseline Score: {baseline_summary.mean_overall_score * 100:.1f}% | Citation Prec: {baseline_summary.mean_citation_precision * 100:.1f}% | Hallucinations: {baseline_summary.hallucination_sample_count}")

    # 4. Run Candidate Degraded Run (Simulating Model/Retriever Churn Regression)
    print("\n[3/4] Running Candidate Experiment: 'v1.1-hallucinating-candidate'...")
    candidate_agent = AgenticRAGAgent(mode=AgentMode.HALLUCINATING)
    candidate_summary = runner.run_suite(
        samples=samples,
        agent=candidate_agent,
        experiment_name="v1.1-candidate-hallucinating",
    )
    print(f"      Candidate Score: {candidate_summary.mean_overall_score * 100:.1f}% | Citation Prec: {candidate_summary.mean_citation_precision * 100:.1f}% | Hallucinations: {candidate_summary.hallucination_sample_count}")

    # 5. Regression Detection
    print("\n[4/4] Performing Automated Regression Analysis...")
    regression = runner.detect_regression(baseline_summary, candidate_summary)

    if regression.is_regression:
        print("      [WARNING] REGRESSION DETECTED!")
        for warn in regression.regression_warnings:
            print(f"        - {warn}")
    else:
        print("      [PASS] No regression detected.")

    # 6. Export Markdown Report
    report_md = EvaluationReporter.generate_markdown_report(candidate_summary, regression)
    with open(args.report_out, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n[COMPLETE] Comprehensive Evaluation Report saved to '{args.report_out}'")
    print("================================================================================\n")


if __name__ == "__main__":
    main()
