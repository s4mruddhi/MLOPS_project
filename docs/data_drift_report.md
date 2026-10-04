# Data & Query Drift Detection Report (Phase 15)

## Overview
- **Reference Queries Baseline:** 20 queries
- **In-Domain Batch Size:** 20 queries
- **Out-of-Domain Batch Size:** 10 queries

---

## 1. In-Domain Query Batch Results
- **Drift Detected:** `False`
- **Overall Drift Ratio:** `0.5`
- **Semantic Embedding Cosine Distance:** `0.0251`
- **Drifted Features Count:** `2 / 4`

---

## 2. Out-of-Domain Shifted Query Batch Results
- **Drift Detected:** `True`
- **Overall Drift Ratio:** `0.5`
- **Semantic Embedding Cosine Distance:** `0.8271`
- **Drifted Features Count:** `2 / 4`

---

## Feature-Level Statistical Breakdowns (Out-of-Domain)
| Feature / Metric | Statistic / Metric Value | Drift Status |
| :--- | :--- | :--- |
| **Word Count (KS-Test)** | p-val=0.3686 | `False` |
| **Character Count (KS-Test)** | p-val=0.9491 | `False` |
| **Vocabulary Jaccard Distance** | dist=0.9365 | `True` |
| **Embedding Cosine Distance** | dist=0.8271 | `True` |
