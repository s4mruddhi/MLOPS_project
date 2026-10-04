"""
Data Pipeline DAG for Automated Data Extraction & Ingestion
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

def extract_data():
    print("Extracting raw document corpus...")

def process_data():
    print("Processing and cleaning text data...")

with DAG(
    'data_pipeline_dag',
    default_args=default_args,
    description='Automated Data Ingestion and Preprocessing Pipeline',
    schedule='@daily',
    catchup=False,
    tags=['data_pipe'],
) as dag:

    t1 = PythonOperator(
        task_id='extract_raw_data',
        python_callable=extract_data,
    )

    t2 = PythonOperator(
        task_id='preprocess_data',
        python_callable=process_data,
    )

    t1 >> t2
