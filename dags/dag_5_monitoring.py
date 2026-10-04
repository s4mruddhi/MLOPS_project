"""
DAG 5: Performance & Latency Monitoring Pipeline
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

def monitor_latency():
    print("Monitoring p95 and p99 query latency metrics...")

def check_hallucination_drift():
    print("Checking hallucination rate and embedding drift metrics...")

with DAG(
    'dag_5_performance_monitoring',
    default_args=default_args,
    description='RAGOps Latency, Throughput & Hallucination Rate Monitoring',
    schedule='@daily',
    catchup=False,
    tags=['monitoring_v1'],
) as dag:

    t1 = PythonOperator(
        task_id='check_api_latency',
        python_callable=monitor_latency,
    )

    t2 = PythonOperator(
        task_id='check_hallucination_drift',
        python_callable=check_hallucination_drift,
    )

    t1 >> t2
