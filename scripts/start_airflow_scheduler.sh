#!/usr/bin/env bash
set -euo pipefail

export PROJECT_ROOT="/mnt/d/mineria data/airflow"
export AIRFLOW_HOME="$PROJECT_ROOT/airflow_home"
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"
export AIRFLOW__CORE__LOAD_EXAMPLES="False"
export AIRFLOW__CORE__DAGS_FOLDER="$AIRFLOW_HOME/dags"

"$PROJECT_ROOT/.venv/bin/airflow" scheduler
