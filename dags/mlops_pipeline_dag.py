"""
MLOps End-to-End Pipeline DAG
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'mlops_student',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def train_model():
    print("Training vector retrieval & reranking models...")

def evaluate_model():
    print("Evaluating trained model metrics and logging to MLflow...")

with DAG(
    'mlops_pipeline_dag',
    default_args=default_args,
    description='MLOps End-to-End Training & Evaluation Pipeline',
    schedule='@weekly',
    catchup=False,
    tags=['mlops_pipe'],
) as dag:

    t1 = PythonOperator(
        task_id='train_retriever_model',
        python_callable=train_model,
    )

    t2 = PythonOperator(
        task_id='evaluate_model_performance',
        python_callable=evaluate_model,
    )

    t1 >> t2
