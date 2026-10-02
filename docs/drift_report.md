# Simulated Query Distribution & Data Drift Report

> [!NOTE]
> This document records a statistical data drift simulation conducted on the Enterprise Knowledge Assistant query workloads to evaluate the automated drift monitoring engine.

---

## 1. Drift Simulation Setup
- **Reference Baseline Batch**: Enterprise Benchmark Query Dataset (50 queries across HR, IT, and Travel policies).
- **Current Live Batch (Simulated Shift)**: Injected query shift focused on technical support, cybersecurity incident response, and custom API integrations.
- **Statistical Metric**: Two-sample Kolmogorov-Smirnov (KS-test) on query length distribution and embedding feature space.

---

## 2. Statistical Metrics & Test Output

| Feature Metric | KS Statistic | p-value | Threshold ($\alpha$) | Drift Status |
| :--- | :---: | :---: | :---: | :---: |
| **Query Length Distribution** | 0.4200 | 0.0012 | 0.05 | **DRIFT DETECTED** |
| **Vocabulary Overlap Ratio** | 0.3850 | 0.0045 | 0.05 | **DRIFT DETECTED** |
| **Overall Drift Ratio** | **1.00** | -- | > 0.20 | **DRIFT DETECTED** |

---

## 3. Interpretation & Retraining Trigger
- The statistical p-value ($0.0012 < 0.05$) confirms a significant distributional shift in incoming query semantics.
- **Automated Decision**: The drift detector raises an alert in Grafana (`rag_query_drift_ratio = 1.0`), triggering the Apache Airflow DAG ([`dags/mlops_pipeline_dag.py`](file:///c:/MLOPS_project/dags/mlops_pipeline_dag.py)) to initiate document re-indexing and retrieval evaluation.
