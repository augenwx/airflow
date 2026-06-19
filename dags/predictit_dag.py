from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/opt/predictit-data-pipeline"))
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from extract_predictit import main as extract_predictit
from load_duckdb import load_parquet_to_duckdb
from transform_to_parquet import main as transform_to_parquet


def transform_task(**context):
    raw_path = context["ti"].xcom_pull(task_ids="extract_predictit")
    return transform_to_parquet(raw_path)


with DAG(
    dag_id="predictit_local_pipeline",
    description="Extract PredictIt data, store raw JSON, convert to Parquet, and expose with DuckDB.",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["predictit", "duckdb", "local-data-lake"],
) as dag:
    extract = PythonOperator(
        task_id="extract_predictit",
        python_callable=extract_predictit,
    )

    transform = PythonOperator(
        task_id="transform_to_parquet",
        python_callable=transform_task,
    )

    load = PythonOperator(
        task_id="load_duckdb",
        python_callable=load_parquet_to_duckdb,
    )

    extract >> transform >> load
