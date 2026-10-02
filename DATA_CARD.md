# Data Card: Enterprise Knowledge Base & Benchmark Corpus

## 1. Dataset Overview
- **Dataset Name**: Enterprise Knowledge Base Corpus (`data/raw/knowledge_docs.json`)
- **Version**: Version 1.0 (Managed with DVC)
- **Domain**: Enterprise Technical Infrastructure, SOC2 Compliance, GDPR Regulations, API Specifications
- **Format**: Structured JSON Document Collection & DVC Vector Chunk Stores

## 2. Document Schema & Descriptions
| Attribute | Data Type | Description |
| :--- | :--- | :--- |
| `doc_id` | String | Unique Document Identifier (e.g. `DOC-SEC-201`, `DOC-GATEWAY-101`) |
| `source_title` | String | Human-readable document title |
| `category` | String | Document category (`API_Infrastructure`, `Security_Compliance`, `Database_Ops`, `Customer_Support`) |
| `text` | String | Text content containing policies, gateway specs, and runbook guidelines |
| `metadata` | Object | Author, version, and document release metadata |

## 3. Data Quality & Schema Validation Rules
- **Schema Validation**: Verified via `DataValidator.validate_documents` (Checking missing keys, duplicate IDs, and text token bounds).
- **Text Length Bounds**: Minimum 15 characters per chunk; zero tolerance for empty documents.

## 4. Anonymization & Security
- All customer PII is excluded from internal documentation.
- Proprietary credentials or API keys are scrubbed prior to vector embedding.

## 5. DVC Data Lineage
- Raw knowledge base corpus tracked via `.dvc` metadata pointers.
- Reproducible MD5 hashes generated for data version verification.
