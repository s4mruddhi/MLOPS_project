"""
Phase 15 Verification Script: Query & Data Drift Detection Pipeline.
"""

import os
import sys
import json
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

from src.monitoring.drift_detector import DataDriftDetector

def main():
    print("==================================================")
    print("PHASE 15 — DATA & QUERY DRIFT DETECTION PIPELINE")
    print("==================================================")

    ref_path = os.path.join(PROJECT_ROOT, "data", "evaluation", "reference_queries.csv")
    in_domain_path = os.path.join(PROJECT_ROOT, "data", "evaluation", "in_domain_current_queries.csv")
    out_of_domain_path = os.path.join(PROJECT_ROOT, "data", "evaluation", "out_of_domain_current_queries.csv")

    assert os.path.exists(ref_path), "reference_queries.csv missing"
    assert os.path.exists(in_domain_path), "in_domain_current_queries.csv missing"
    assert os.path.exists(out_of_domain_path), "out_of_domain_current_queries.csv missing"

    ref_df = pd.read_csv(ref_path)
    in_domain_df = pd.read_csv(in_domain_path)
    out_of_domain_df = pd.read_csv(out_of_domain_path)

    print(f"Loaded Reference Baseline Queries:   {len(ref_df)} queries")
    print(f"Loaded In-Domain Current Queries:    {len(in_domain_df)} queries")
    print(f"Loaded Out-of-Domain Current Queries: {len(out_of_domain_df)} queries")

    detector = DataDriftDetector(ref_df)

    # 1. In-Domain Drift Evaluation (Expected: Low/No Drift)
    print("\n[Step 1] Evaluating In-Domain Query Batch Drift...")
    in_domain_res = detector.detect_feature_drift(in_domain_df)
    print(f"  Drift Detected:        {in_domain_res['drift_detected']}")
    print(f"  Overall Drift Ratio:   {in_domain_res['overall_drift_ratio']}")
    print(f"  Semantic Distance:     {in_domain_res['semantic_drift_score']}")

    # 2. Out-of-Domain Drift Evaluation (Expected: High Drift)
    print("\n[Step 2] Evaluating Out-of-Domain Shifted Query Batch Drift...")
    out_of_domain_res = detector.detect_feature_drift(out_of_domain_df)
    print(f"  Drift Detected:        {out_of_domain_res['drift_detected']}")
    print(f"  Overall Drift Ratio:   {out_of_domain_res['overall_drift_ratio']}")
    print(f"  Semantic Distance:     {out_of_domain_res['semantic_drift_score']}")

    assert out_of_domain_res["drift_detected"] is True, "Out-of-domain query batch must trigger drift detection!"

    # 3. Export Reports
    report_json_path = os.path.join(PROJECT_ROOT, "data", "evaluation", "drift_report.json")
    report_md_path = os.path.join(PROJECT_ROOT, "docs", "data_drift_report.md")

    full_report = {
        "reference_sample_size": len(ref_df),
        "in_domain_evaluation": in_domain_res,
        "out_of_domain_evaluation": out_of_domain_res,
    }

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    markdown_report = f"""# Data & Query Drift Detection Report (Phase 15)

## Overview
- **Reference Queries Baseline:** {len(ref_df)} queries
- **In-Domain Batch Size:** {len(in_domain_df)} queries
- **Out-of-Domain Batch Size:** {len(out_of_domain_df)} queries

---

## 1. In-Domain Query Batch Results
- **Drift Detected:** `{in_domain_res['drift_detected']}`
- **Overall Drift Ratio:** `{in_domain_res['overall_drift_ratio']}`
- **Semantic Embedding Cosine Distance:** `{in_domain_res['semantic_drift_score']}`
- **Drifted Features Count:** `{in_domain_res['drifted_features_count']} / {in_domain_res['total_features']}`

---

## 2. Out-of-Domain Shifted Query Batch Results
- **Drift Detected:** `{out_of_domain_res['drift_detected']}`
- **Overall Drift Ratio:** `{out_of_domain_res['overall_drift_ratio']}`
- **Semantic Embedding Cosine Distance:** `{out_of_domain_res['semantic_drift_score']}`
- **Drifted Features Count:** `{out_of_domain_res['drifted_features_count']} / {out_of_domain_res['total_features']}`

---

## Feature-Level Statistical Breakdowns (Out-of-Domain)
| Feature / Metric | Statistic / Metric Value | Drift Status |
| :--- | :--- | :--- |
| **Word Count (KS-Test)** | p-val={out_of_domain_res['feature_details']['word_count_distribution']['p_value']} | `{out_of_domain_res['feature_details']['word_count_distribution']['drift_detected']}` |
| **Character Count (KS-Test)** | p-val={out_of_domain_res['feature_details']['char_count_distribution']['p_value']} | `{out_of_domain_res['feature_details']['char_count_distribution']['drift_detected']}` |
| **Vocabulary Jaccard Distance** | dist={out_of_domain_res['feature_details']['vocabulary_drift']['jaccard_distance']} | `{out_of_domain_res['feature_details']['vocabulary_drift']['drift_detected']}` |
| **Embedding Cosine Distance** | dist={out_of_domain_res['feature_details']['semantic_embedding_drift']['cosine_distance']} | `{out_of_domain_res['feature_details']['semantic_embedding_drift']['drift_detected']}` |
"""

    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print(f"\n[Step 3] Reports successfully generated:\n  - {report_json_path}\n  - {report_md_path}")
    print("\n==================================================")
    print("PHASE 15 DRIFT DETECTION PIPELINE VERIFIED SUCCESSFUL!")
    print("==================================================")

if __name__ == "__main__":
    main()
