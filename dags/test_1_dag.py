"""
Test 1 DAG for Airflow Pipeline Verification
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

def test_task():
    print("Running test_1_dag task successfully!")

with DAG(
    'test_1_dag',
    default_args=default_args,
    description='Test 1 DAG verification',
    schedule='@daily',
    catchup=False,
    tags=['test_1'],
) as dag:

    run_test = PythonOperator(
        task_id='execute_test_1',
        python_callable=test_task,
    )
