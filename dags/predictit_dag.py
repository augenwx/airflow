from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/opt/predictit-data-pipeline"))
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from config import DATA_WAREHOUSE
from extract_predictit import main as extract_predictit
from load_duckdb import main as load_duckdb_main
from load_snowflake import main as load_snowflake_main
from transform_to_parquet import main as transform_to_parquet

DBT_BIN = os.getenv("DBT_BIN", str(PROJECT_ROOT / ".venv" / "bin" / "dbt"))
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt" / "predictit_dbt"
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", str(PROJECT_ROOT / "dbt"))


def transform_task(**context):
    raw_path = context["ti"].xcom_pull(task_ids="extract_predictit")
    return transform_to_parquet(raw_path)


def load_warehouse_task(**context):
    parquet_paths = context["ti"].xcom_pull(task_ids="transform_to_parquet")
    if DATA_WAREHOUSE == "duckdb":
        return load_duckdb_main()
    if DATA_WAREHOUSE == "snowflake":
        return load_snowflake_main(parquet_paths)
    raise ValueError("DATA_WAREHOUSE must be either 'snowflake' or 'duckdb'.")


with DAG(
    dag_id="predictit_local_pipeline",
    description="Extract PredictIt data, convert to Parquet, load Snowflake, and run dbt.",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["predictit", "snowflake", "airflow", "dbt"],
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
        task_id="load_warehouse",
        python_callable=load_warehouse_task,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd '{DBT_PROJECT_DIR}' && '{DBT_BIN}' run --profiles-dir '{DBT_PROFILES_DIR}'",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd '{DBT_PROJECT_DIR}' && '{DBT_BIN}' test --profiles-dir '{DBT_PROFILES_DIR}'",
    )

    extract >> transform >> load >> dbt_run >> dbt_test
