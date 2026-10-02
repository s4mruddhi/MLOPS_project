"""
Apache Airflow DAG for Continuous Enterprise MLOps Pipeline Automation.
"""

from datetime import datetime, timedelta
import os
import sys

# Add project root to sys.path for Airflow runtime
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False


def task_ingest_data():
    from src.data.ingestion import ingest_data
    df = ingest_data()
    print(f"Airflow Task [Data Ingestion] completed. Ingested {len(df)} rows.")


def task_validate_data():
    import pandas as pd
    from src.config import RAW_DATA_PATH
    from src.data.validation import DataValidator

    df = pd.read_csv(RAW_DATA_PATH)
    is_valid, errors = DataValidator.validate(df)
    if not is_valid:
        raise ValueError(f"Airflow Task [Data Validation] FAILED: {errors}")
    print("Airflow Task [Data Validation] PASSED successfully.")


def task_preprocess_data():
    import pandas as pd
    from src.config import RAW_DATA_PATH
    from src.data.preprocessing import preprocess_data

    df = pd.read_csv(RAW_DATA_PATH)
    X_trans, y, _, _ = preprocess_data(df, fit=True)
    print(f"Airflow Task [Preprocessing] completed. Processed shape: {X_trans.shape}")


def task_train_and_register():
    from src.models.train import run_training_pipeline
    metrics, best_name = run_training_pipeline()
    print(f"Airflow Task [Training & Registration] completed. Champion: '{best_name}', Metrics: {metrics}")


if AIRFLOW_AVAILABLE:
    default_args = {
        "owner": "mlops_team",
        "depends_on_past": False,
        "start_date": datetime(2026, 1, 1),
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    dag = DAG(
        "enterprise_churn_mlops_pipeline",
        default_args=default_args,
        description="Automated End-to-End MLOps Training, Quality Gate & Model Registration Pipeline",
        schedule_interval="@weekly",
        catchup=False,
    )

    t1 = PythonOperator(task_id="ingest_data", python_callable=task_ingest_data, dag=dag)
    t2 = PythonOperator(task_id="validate_data", python_callable=task_validate_data, dag=dag)
    t3 = PythonOperator(task_id="preprocess_data", python_callable=task_preprocess_data, dag=dag)
    t4 = PythonOperator(task_id="train_and_register_model", python_callable=task_train_and_register, dag=dag)

    t1 >> t2 >> t3 >> t4
