"""
Knowledge Base Data Ingestion Module for Enterprise RAG Assistant.
Ingests enterprise knowledge documents, technical runbooks, and compliance policies.
"""

import os
import json
import pandas as pd
from typing import List, Dict, Any
from src.config import RAW_DOCS_PATH, set_seed


def generate_enterprise_knowledge_base() -> List[Dict[str, Any]]:
    """Generates enterprise corpus of technical runbooks, SOC2 policies, and API gateway specs."""
    set_seed(42)

    documents = [
        {
            "doc_id": "DOC-GATEWAY-101",
            "source_title": "Enterprise API Gateway Architecture & Limits",
            "category": "API_Infrastructure",
            "text": "Enterprise API Gateway specifies a maximum allowed API request payload size of 10 MB for standard REST endpoints. Streaming gRPC and WebSocket endpoints permit up to 50 MB payload buffer size.",
            "metadata": {"author": "Infrastructure Team", "version": "2025.1"},
        },
        {
            "doc_id": "DOC-SEC-201",
            "source_title": "SOC2 Type II Audit & Log Retention Policy",
            "category": "Security_Compliance",
            "text": "Security audit logs, system access logs, and administrative trace logs must be securely archived and retained for at least 7 years to satisfy SOC2 Type II compliance audit regulations.",
            "metadata": {"author": "Compliance Office", "version": "3.2"},
        },
        {
            "doc_id": "DOC-COMP-305",
            "source_title": "GDPR Compliance & Data Privacy Standard",
            "category": "Security_Compliance",
            "text": "GDPR Article 17 Right to Erasure mandates that customer PII data must be permanently erased from all production and backup stores within 30 calendar days upon receipt of a valid deletion request.",
            "metadata": {"author": "Legal Dept", "version": "4.0"},
        },
        {
            "doc_id": "DOC-PG-PROD-2025",
            "source_title": "PostgreSQL 2025 Production Tuning Guide",
            "category": "Database_Ops",
            "text": "Idle connection timeout MUST be set to 30 seconds for all PostgreSQL production pools to prevent connection starvation under peak loads.",
            "metadata": {"author": "DBA Team", "version": "2025.2"},
        },
        {
            "doc_id": "DOC-REFUND-POL",
            "source_title": "Customer Refund Policy 2024",
            "category": "Customer_Support",
            "text": "Subscriptions cancelled within 14 days of purchase qualify for a 100% full refund. Cancellations past 14 days receive a pro-rated credit refund applied to the account balance.",
            "metadata": {"author": "Billing Ops", "version": "1.8"},
        },
        {
            "doc_id": "DOC-DB-OPS-501",
            "source_title": "Database Monitoring & Cluster Metrics Runbook",
            "category": "Database_Ops",
            "text": "Database metrics should be retrieved using the cluster status tool. Primary node CPU utilization thresholds above 80% require immediate auto-scaling alerts.",
            "metadata": {"author": "SRE Team", "version": "5.1"},
        },
    ]

    return documents


def ingest_data(output_path: str = RAW_DOCS_PATH) -> List[Dict[str, Any]]:
    """Ingests enterprise document corpus and saves to raw JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    docs = generate_enterprise_knowledge_base()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)

    print(f"[Ingestion] Successfully ingested {len(docs)} enterprise documents into '{output_path}'.")
    return docs


if __name__ == "__main__":
    ingest_data()
