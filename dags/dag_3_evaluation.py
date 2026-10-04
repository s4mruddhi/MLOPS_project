"""
DAG 3: RAG Evaluation Pipeline (Faithfulness & Answer Relevancy)
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

def evaluate_retrieval():
    print("Evaluating MRR, Hit Rate@K, and Precision@K...")

def evaluate_generation():
    print("Evaluating Faithfulness (NLI) and Answer Relevancy...")

with DAG(
    'dag_3_rag_evaluation',
    default_args=default_args,
    description='RAGOps Retrieval & LLM Generation Quality Evaluation',
    schedule='@daily',
    catchup=False,
    tags=['evaluation_v1'],
) as dag:

    t1 = PythonOperator(
        task_id='eval_retrieval_quality',
        python_callable=evaluate_retrieval,
    )

    t2 = PythonOperator(
        task_id='eval_generation_quality',
        python_callable=evaluate_generation,
    )

    t1 >> t2
