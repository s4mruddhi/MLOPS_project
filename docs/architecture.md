# RAGOps: Monitored Enterprise Knowledge Assistant Architecture

## 1. Overview
The **RAGOps: Monitored Enterprise Knowledge Assistant** is an end-to-end, production-oriented system built to answer employee and technical support questions using **only verified organizational documents**. It combines document version control (DVC), vector indexing (ChromaDB), automated pipeline orchestration (Apache Airflow), experiment tracking (MLflow), REST serving (FastAPI), CI/CD automation (GitHub Actions), observability (Prometheus + Grafana), Responsible AI auditing (SHAP + NLI Citation Entailment), and AWS Cloud integration (S3, SageMaker, CloudWatch).

---

## 2. End-to-End System Architecture Diagram

```mermaid
flowchart TD
    subgraph Layer1["1. Raw Document & Versioning Layer"]
        A["Verified Org Docs (PDF, TXT, JSON)"] --> B["DVC (Document Versioning)"]
        B --> C["AWS S3 Remote (s3://bucket/raw-documents)"]
    end

    subgraph Layer2["2. Automated Airflow Pipeline & Processing"]
        C --> D["Airflow Ingestion & Schema Validation"]
        D --> E["Metadata Tagging & Clean Chunking"]
        E --> F["Sentence Transformers Embedding"]
        F --> G["ChromaDB Vector Store / FAISS"]
    end

    subgraph Layer3["3. Retrieval Experiments & MLflow Tracking"]
        G --> H1["TF-IDF Baseline"]
        G --> H2["BM25 Candidate"]
        G --> H3["Semantic Vector Candidate"]
        H1 & H2 & H3 --> I["Retrieval & Groundedness Evaluator"]
        I --> J["MLflow Tracking & Model Registry"]
        J --> K["Quality Gate Check"]
    end

    subgraph Layer4["4. REST Serving & Responsible AI"]
        K --> L["FastAPI REST Prediction Service"]
        L --> M["Grounded Answer + Citation Entailment"]
        L --> N["NLI Citation Explainer & SHAP"]
    end

    subgraph Layer5["5. Observability & Cloud Monitoring"]
        L --> O["Prometheus Metrics Scraper"]
        O --> P["Grafana Dashboard"]
        L --> Q["AWS CloudWatch Logs"]
        L --> R["Query & Embedding Drift Detector"]
        R --> S["Re-Indexing / Retraining Decision"]
    end
```

---

## 3. Document Processing & Ingestion Pipeline

```mermaid
flowchart LR
    A["Raw Document (.pdf, .txt)"] --> B["Document Validator"]
    B -->|Valid| C["Metadata Extractor (id, title, dept, version)"]
    B -->|Corrupted/Invalid| D["Validation Alert Log"]
    C --> E["Configurable Chunker (chunk_size, overlap)"]
    E --> F["Sentence Transformer Embedding"]
    F --> G["ChromaDB Collection Versioning"]
```

---

## 4. RAG Retrieval & Citation Generation Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User as Employee / Support User
    participant API as FastAPI REST Service
    participant DB as ChromaDB Vector Store
    participant NLI as Citation Verifier
    participant LLM as LLM / Agent Generator
    participant ML as MLflow & Prometheus

    User->>API: POST /query {"question": "...", "top_k": 3}
    API->>DB: Query Top-K Chunks with Metadata Filtering
    DB-->>API: Return Relevant Chunks + Scores + Document Metadata
    API->>LLM: Send Query + Grounded Context
    LLM-->>API: Return Answer with Inline Citations [DOC-XXX]
    API->>NLI: Evaluate Claim-to-Source Entailment & Groundedness
    NLI-->>API: Groundedness Score & Unsupported Claim Flag
    API->>ML: Log Request Latency, Groundedness Score & Metrics
    API-->>User: Return Answer + Citations + Groundedness Score
```

---

## 5. AWS Cloud Architecture

```mermaid
flowchart TD
    subgraph AWS["AWS Cloud Infrastructure"]
        S3["AWS S3 Bucket (s3://ragops-bucket/)"]
        S3_RAW["s3://ragops-bucket/raw-documents/"]
        S3_DVC["s3://ragops-bucket/dvc/"]
        S3_EMB["s3://ragops-bucket/embeddings/"]
        S3_MLF["s3://ragops-bucket/mlflow/"]
        
        SM["AWS SageMaker Job (Embedding/Retrieval Benchmark)"]
        CW["AWS CloudWatch Structured Logs"]
    end

    S3 --> S3_RAW & S3_DVC & S3_EMB & S3_MLF
    SM -->|Inputs| S3_RAW
    SM -->|Artifacts| S3_EMB
    FastAPI["FastAPI REST App"] -->|Logs| CW
```

---

## 6. Key Component Specifications
- **Raw Document Layer**: `data/raw/` versioned with DVC.
- **Vector Storage**: ChromaDB persistent local/S3 indexed collection.
- **Retrieval Baseline vs Candidates**: TF-IDF (Baseline), BM25 (Candidate 1), SentenceTransformer `all-MiniLM-L6-v2` (Candidate 2).
- **Prompt Versioning**: Standardized under `prompts/` (`system_v1.txt`, `answer_v1.txt`, `fallback_v1.txt`).
- **Unanswerable Questions Policy**: System checks grounding score and explicitly responds: *"I could not find sufficient information in the verified organizational documents."*
- **Monitoring & Observability**: Prometheus scraping `rag_*` metrics, Grafana visual dashboards, and KS-test query distribution drift detection.
