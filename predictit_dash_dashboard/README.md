# PredictIt Dash Dashboard

Dashboard web en Dash usando DuckDB.

## Ejecutar desde Linux/WSL

```bash
cd "/mnt/d/mineria data/airflow/predictit_dash_dashboard"
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre:

```text
http://localhost:8050
```

Por defecto busca primero:

```text
/mnt/d/mineria data/airflow/data/warehouse/predictit_bi.duckdb
/mnt/d/mineria data/airflow/data/warehouse/predictit.duckdb
```

Tambien puedes fijar la ruta:

```bash
export PREDICTIT_DUCKDB_PATH="/mnt/d/mineria data/airflow/data/warehouse/predictit_bi.duckdb"
python app.py
```
