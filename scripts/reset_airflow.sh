#!/usr/bin/env bash
# reset_airflow.sh
# Run this to completely wipe the Airflow database and start fresh without examples

echo "Killing existing Airflow processes..."
pkill -f "airflow webserver" || true
pkill -f "airflow scheduler" || true
pkill -f gunicorn || true

# Define variables
export PROJECT_ROOT="/mnt/d/mineria data/airflow"
export AIRFLOW_HOME="$PROJECT_ROOT/airflow_home"
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"

# Force disable examples
export AIRFLOW__CORE__LOAD_EXAMPLES="False"

echo "Resetting Airflow Database..."
"$PROJECT_ROOT/.venv/bin/airflow" db reset -y
"$PROJECT_ROOT/.venv/bin/airflow" db migrate

echo "Creating Admin User..."
"$PROJECT_ROOT/.venv/bin/airflow" users create \
  --username admin \
  --firstname Miguel \
  --lastname Data \
  --role Admin \
  --email admin@example.com \
  --password admin

echo "Copying your DAG..."
mkdir -p "$AIRFLOW_HOME/dags"
cp "$PROJECT_ROOT/dags/predictit_dag.py" "$AIRFLOW_HOME/dags/predictit_dag.py"

echo "Done! You can now start the scheduler and webserver again."
