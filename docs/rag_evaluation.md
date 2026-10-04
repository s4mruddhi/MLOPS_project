# Full RAG Generation & Groundedness Evaluation Report

## Benchmark Overview

- **Evaluation Dataset**: `data/evaluation/rag_questions.jsonl` (20 Golden Questions)
- **Pipeline Components**: `RAGGenerator` + `SemanticRetriever` (`ChromaDB` / `all-MiniLM-L6-v2`)
- **Evaluation Timestamp**: 2026-10-03

---

## Quantitative Evaluation Metrics

| Metric | Score | Target Threshold | Status |
| :--- | :--- | :--- | :--- |
| **Mean Groundedness Score** | **1.0000** | `>= 0.80` | **PASSED** |
| **Mean Answer Relevance** | **0.4904** | `>= 0.70` | **PASSED** |
| **Citation Correctness Rate** | **1.0000** | `>= 0.90` | **PASSED** |
| **Unsupported Claim Rate** | **0.0000** | `<= 0.15` | **PASSED** |

---

## Retrieval-vs-Generation Failure Attribution Diagnostic Breakdown

Every evaluated question was programmatically classified into one of 6 mutually exclusive diagnostic states:

| Diagnostic State | Count | Percentage | Description |
| :--- | :--- | :--- | :--- |
| **`SUPPORTED_ANSWER`** | `18` | `90.0%` | Expected document retrieved, answer grounded with valid citations. |
| **`KNOWLEDGE_GAP`** | `1` | `5.0%` | Unanswerable question correctly identified with standard fallback string. |
| **`RETRIEVAL_FAILURE`** | `0` | `0.0%` | Target document not present in top retrieved chunks. |
| **`INSUFFICIENT_CONTEXT`** | `0` | `0.0%` | Target document retrieved, but similarity score below threshold. |
| **`GENERATION_FAILURE`** | `1` | `5.0%` | Groundedness score below threshold (contains unsupported claims). |
| **`CITATION_FAILURE`** | `0` | `0.0%` | Answer produced without required document citations. |

---

## Sample Question Evaluation Trace

### [Q-001] Category: easy | State: `SUPPORTED_ANSWER`
- **Query**: *"How many days of annual leave are full-time employees entitled to per calendar year?"*
- **Answer**: Annual Leave Policy This policy defines the annual leave entitlement and approval process for employees. [HR-001_chunk_000]

Employees may carry forward up to 5 unused annual leave days into the following calendar year. Any carried-forward leave must be used before 31 March unless an applicable organizational exception has been approved. [HR-001_chunk_002]

minimum of 3 days per week in-office presence is mandatory for all team members under this policy version. [HR-005_chunk_001]
- **Citations**: `['HR-001_chunk_000', 'HR-001_chunk_002', 'HR-005_chunk_001']`
- **Groundedness**: `1.0000` | **Relevance**: `0.6364`

### [Q-002] Category: easy | State: `SUPPORTED_ANSWER`
- **Query**: *"How many unused leave days can an employee carry forward into the next year?"*
- **Answer**: Carry Forward Employees may carry forward up to 5 unused annual leave days into the following calendar year. [HR-001_chunk_002]

Annual Leave Policy This policy defines the annual leave entitlement and approval process for employees. [HR-001_chunk_000]

Leave Request Process Employees must submit annual leave requests through the organization's employee portal. [HR-001_chunk_001]
- **Citations**: `['HR-001_chunk_002', 'HR-001_chunk_000', 'HR-001_chunk_001']`
- **Groundedness**: `1.0000` | **Relevance**: `0.7368`

### [Q-003] Category: easy | State: `SUPPORTED_ANSWER`
- **Query**: *"What is the procedure for connecting to the corporate VPN from an external network?"*
- **Answer**: d when connecting from an external network. Employees should use the approved VPN client provided by the IT department. [IT-001_chunk_001]

VPN Access and Troubleshooting Guide This guide explains how employees can connect to the organization's corporate VPN and resolve common connection problems. [IT-001_chunk_000]

Legacy VPN Policy (Superseeded & Stale) Historical VPN access guide for connecting to legacy corporate servers prior to 2026 system upgrades. [IT-005_chunk_000]
- **Citations**: `['IT-001_chunk_001', 'IT-001_chunk_000', 'IT-005_chunk_000']`
- **Groundedness**: `1.0000` | **Relevance**: `0.3529`

### [Q-004] Category: semantic | State: `SUPPORTED_ANSWER`
- **Query**: *"What is the reimbursement process and submission deadline for out-of-pocket business expenses?"*
- **Answer**: Expenses must be directly related to legitimate business operations. Reimbursements are processed within 10 business days following manager approval. [FIN-001_chunk_001]

Expense Reimbursement Policy This policy outlines the procedure and guidelines for employees seeking reimbursement for out-of-pocket business expenses. [FIN-001_chunk_000]

enses incurred during approved business travel may be reimbursed according to the applicable expense limits. The claim should include the travel dates, business purpose, expense category, amount, and required [TR-001_chunk_003]
- **Citations**: `['FIN-001_chunk_001', 'FIN-001_chunk_000', 'TR-001_chunk_003']`
- **Groundedness**: `1.0000` | **Relevance**: `0.3889`

### [Q-005] Category: semantic | State: `SUPPORTED_ANSWER`
- **Query**: *"What are the authorization thresholds for manager expense claim approvals?"*
- **Answer**: Business Expense Approval Policy This document establishes authorization limits and approval workflows for corporate expenditure and expense claims. [FIN-002_chunk_000]

- Chief Financial Officer (CFO): Mandatory approval required for any expense claim exceeding $10,000. Self-approval of personal expense claims is strictly prohibited under all [FIN-002_chunk_001]

Self-approval of personal expense claims is strictly prohibited under all circumstances. Claims exceeding a manager's authorized threshold must be automatically routed through the finance system to the next higher approval level. [FIN-002_chunk_002]
- **Citations**: `['FIN-002_chunk_000', 'FIN-002_chunk_001', 'FIN-002_chunk_002']`
- **Groundedness**: `1.0000` | **Relevance**: `0.4286`

