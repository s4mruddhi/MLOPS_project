# Continuous Agentic RAG Evaluation Report: `v1.1-candidate-hallucinating`
**Agent Mode**: `hallucinating` | **Total Samples Evaluated**: `5`

## Executive Metrics Summary
| Metric | Value | Target | Status |
| :--- | :---: | :---: | :---: |
| **Overall Correctness Score** | `77.8%` | ≥ 80.0% | `WARN` |
| **Context Precision** | `100.0%` | ≥ 75.0% | `PASS` |
| **Context Recall** | `100.0%` | ≥ 75.0% | `PASS` |
| **Citation Precision** | `36.7%` | ≥ 85.0% | `FAIL` |
| **Unsupported Citation Rate** | `50.0%` | ≤ 10.0% | `FAIL` |
| **Tool Selection Accuracy** | `100.0%` | ≥ 90.0% | `PASS` |
| **Hallucination Incidents** | `5` / 5 | 0 | `FAIL` |
| **Avg Query Latency** | `0.0 ms` | < 2000 ms | `PASS` |

## Regression Detection Analysis
> [!WARNING]
> **REGRESSION DETECTED** in candidate run `v1.1-candidate-hallucinating` compared to baseline `v1.0-baseline-accurate`.
> - Overall Score dropped by 8.17% (from 0.86 to 0.7783)
> - Citation Precision dropped by 23.33% (from 0.6 to 0.3667)
> - Hallucination count increased by +2 samples (from 3 to 5)

## Sample-Level Evaluation Breakdown
| Sample ID | Query Snippet | Context Prec | Citation Prec | Tool Acc | Latency | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `SAMPLE-001` | What is the maximum allowed API req... | `100%` | `50%` | `100%` | `0 ms` | `FAIL` |
| `SAMPLE-002` | Compare our SOC2 compliance data re... | `100%` | `67%` | `100%` | `0 ms` | `FAIL` |
| `SAMPLE-003` | Check the database status for clust... | `100%` | `0%` | `100%` | `0 ms` | `FAIL` |
| `SAMPLE-004` | What is the recommended timeout set... | `100%` | `33%` | `100%` | `0 ms` | `FAIL` |
| `SAMPLE-005` | What is the policy for processing c... | `100%` | `33%` | `100%` | `0 ms` | `FAIL` |
