from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/mnt/d/mineria data/airflow"))
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from extract_predictit import main as extract_predictit
from load_duckdb import main as load_duckdb_main
from transform_to_parquet import main as transform_to_parquet


def transform_task(**context):
    raw_path = context["ti"].xcom_pull(task_ids="extract_predictit")
    return transform_to_parquet(raw_path)


with DAG(
    dag_id="predictit_local_pipeline",
    description="Extract PredictIt data, store raw JSON, convert to Parquet, expose with DuckDB, and run dbt.",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["predictit", "duckdb", "local-data-lake", "dbt"],
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
        python_callable=load_duckdb_main,
    )

    # Note: we use double quotes and escape to ensure proper path resolution if PROJECT_ROOT contains spaces
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd '{PROJECT_ROOT}/dbt/predictit_dbt' && ../../.venv/bin/dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd '{PROJECT_ROOT}/dbt/predictit_dbt' && ../../.venv/bin/dbt test",
    )

    extract >> transform >> load >> dbt_run >> dbt_test
