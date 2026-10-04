"""
Unit and Integration Tests for Phase 11: Airflow DAG & Quality Gate.
"""

import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from dags.ragops_pipeline_dag import (
    task_ingest_documents,
    task_validate_documents,
    task_quality_gate,
    AIRFLOW_AVAILABLE
)

# 1. Ingestion Task Test
def test_task_ingest_documents():
    count = task_ingest_documents()
    assert count == 27

# 2. Validation Task Test
def test_task_validate_documents():
    # Should complete without error
    task_validate_documents()

# 3. Quality Gate Task Test
def test_task_quality_gate():
    # Should pass under current dataset metrics (Groundedness = 1.0, Citation Rate = 1.0)
    task_quality_gate()

# 4. Airflow DAG Module Import Test
def test_airflow_dag_import():
    from dags import ragops_pipeline_dag
    assert hasattr(ragops_pipeline_dag, "task_ingest_documents")
    assert hasattr(ragops_pipeline_dag, "task_quality_gate")
    assert hasattr(ragops_pipeline_dag, "task_register_version")
