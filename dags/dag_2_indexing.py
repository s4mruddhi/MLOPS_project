"""
DAG 2: Vector Indexing & Embedding Pipeline for RAGOps
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

def generate_embeddings():
    print("Generating dense vector embeddings for document chunks...")

def update_vector_store():
    print("Upserting vector embeddings into FAISS/Chroma database...")

with DAG(
    'dag_2_vector_indexing',
    default_args=default_args,
    description='RAGOps Dense Vector Embedding & FAISS Indexing',
    schedule='@daily',
    catchup=False,
    tags=['indexing_v1'],
) as dag:

    t1 = PythonOperator(
        task_id='embed_chunks',
        python_callable=generate_embeddings,
    )

    t2 = PythonOperator(
        task_id='upsert_vector_index',
        python_callable=update_vector_store,
    )

    t1 >> t2
