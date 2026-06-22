#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
export AIRFLOW_HOME="$PROJECT_ROOT/airflow_home"
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"

if [ -f "$PROJECT_ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +a
fi

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
