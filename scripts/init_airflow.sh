#!/usr/bin/env bash
set -euo pipefail

# Define variables
export PROJECT_ROOT="/mnt/d/mineria data/airflow"
export AIRFLOW_HOME="$PROJECT_ROOT/airflow_home"
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"

# Run database migration
"$PROJECT_ROOT/.venv/bin/airflow" db migrate

# Create Admin User
"$PROJECT_ROOT/.venv/bin/airflow" users create \
  --username admin \
  --firstname Miguel \
  --lastname Data \
  --role Admin \
  --email admin@example.com \
  --password admin || true

# Copy DAG file to airflow home
mkdir -p "$AIRFLOW_HOME/dags"
cp "$PROJECT_ROOT/dags/predictit_dag.py" "$AIRFLOW_HOME/dags/predictit_dag.py"

echo "Airflow successfully initialized!"
