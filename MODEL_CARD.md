# Model Card: Production-Ready Enterprise Knowledge Assistant (`EnterpriseRAGAssistant`)

## 1. Model Details
- **Model Developer**: Enterprise RAG Ops Engineering Team
- **Model Version**: `v1.0.0` (MLflow Model Registry Alias: `Production`)
- **Model Architecture**: Reranked Hybrid Semantic Vector Retriever + Citation Entailment Engine (`scikit-learn` & `NLI`)
- **License**: Proprietary / Enterprise Internal Use
- **Release Date**: October 2026

## 2. Intended Use & Application
- **Primary Intended Use**: Real-time evaluation and answering of internal enterprise knowledge queries (SOC2 policies, API specs, database runbooks, compliance standards) with verifiable claim-level inline citations (`[DOC-XXX]`).
- **Primary Users**: Enterprise Employees, Customer Support Engineers, Compliance Officers.
- **Out-of-Scope Use Cases**: Automated execution of privileged system modifications without explicit human authorization.

## 3. Training & Benchmark Data
- **Corpus**: Enterprise Technical Runbooks & Compliance Documents (`data/raw/knowledge_docs.json`).
- **Evaluation Dataset**: Enterprise Multi-Step Benchmark Suite (`data/synthetic_benchmark.json`).
- **Sample Categories**: Single-Doc Lookup, Multi-Doc Reasoning Synthesis, Tool-Augmented RAG, Noisy Contexts, and Indirect Prompt Injection Security test cases.

## 4. Model Performance & Evaluation Metrics
- **Context Precision**: 100.0%
- **Context Recall**: 100.0%
- **Citation Precision**: 100.0%
- **Answer Faithfulness Score**: 100.0%
- **p95 Inference Latency**: < 45.0 ms
- **Throughput Capacity**: > 450 requests/sec

## 5. Responsible AI & Citation Entailment Audit
- **Citation Entailment Engine**: Automatically verifies whether each sentence claim in an answer is explicitly supported by text in cited document chunks (`ENTAILED` vs `UNSUPPORTED`).
- **Hallucination Mitigation**: Unsupported claims and missing citations are flagged with real-time alerts.
- **Security Audit**: Indirect prompt injection payloads embedded in retrieved chunks are intercepted and neutralized.

## 6. Risk Factors & Operational Maintenance
- Retriever re-indexing required whenever enterprise knowledge base documents are added or updated (`dags/mlops_pipeline_dag.py`).
- Query distribution drift tracked continuously via `POST /drift-check` and Prometheus alerting (`model_data_drift_ratio`).
