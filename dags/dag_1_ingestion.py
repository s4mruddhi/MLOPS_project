"""
DAG 1: Document Ingestion Pipeline for RAGOps
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'mlops_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def ingest_documents():
    print("Ingesting enterprise documents into staging...")

def parse_metadata():
    print("Extracting document metadata and chunking text...")

with DAG(
    'dag_1_document_ingestion',
    default_args=default_args,
    description='RAGOps Document Ingestion & Chunking Pipeline',
    schedule='@daily',
    catchup=False,
    tags=['ingestion_v1'],
) as dag:

    t1 = PythonOperator(
        task_id='ingest_docs',
        python_callable=ingest_documents,
    )

    t2 = PythonOperator(
        task_id='parse_chunk_docs',
        python_callable=parse_metadata,
    )

    t1 >> t2
