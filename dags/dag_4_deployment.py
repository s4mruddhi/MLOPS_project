"""
DAG 4: Automated Model & Retriever Deployment Pipeline
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

def log_mlflow_model():
    print("Registering new Retriever & Synthesizer models in MLflow Model Registry...")

def deploy_fastapi():
    print("Deploying containerized FastAPI endpoint with updated index...")

with DAG(
    'dag_4_model_deployment',
    default_args=default_args,
    description='RAGOps Model Registration & Automated Deployment Pipeline',
    schedule='@weekly',
    catchup=False,
    tags=['deployment_v1'],
) as dag:

    t1 = PythonOperator(
        task_id='register_mlflow_model',
        python_callable=log_mlflow_model,
    )

    t2 = PythonOperator(
        task_id='deploy_api_service',
        python_callable=deploy_fastapi,
    )

    t1 >> t2
