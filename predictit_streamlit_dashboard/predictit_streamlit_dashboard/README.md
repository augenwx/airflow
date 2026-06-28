# PredictIt Streamlit Dashboard

Dashboard web en Streamlit usando `predictit.duckdb`.

## Estructura

```text
predictit_streamlit_dashboard/
├── app.py
├── requirements.txt
└── README.md
```

## Instalación

```bash
cd predictit_streamlit_dashboard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configurar ruta DuckDB

Edita `app.py` y cambia:

```python
DEFAULT_DB_PATH = r"D:\mineria data\airflow\data\warehouse\predictit_bi.duckdb"
```

Recomendado: usa una copia de lectura para BI, no el archivo que Airflow está escribiendo.

Ejemplo:

```bat
copy "D:\mineria data\airflow\data\warehouse\predictit.duckdb" ^
     "D:\mineria data\airflow\data\warehouse\predictit_bi.duckdb"
```

También puedes usar variable de entorno:

```bat
set PREDICTIT_DUCKDB_PATH=D:\mineria data\airflow\data\warehouse\predictit_bi.duckdb
```

## Ejecutar

```bash
streamlit run app.py
```

Abre:

```text
http://localhost:8501
```

## Páginas incluidas

1. Executive Overview
2. Historical Trends
3. Risk & Anomalies
4. Contract Detail

## Tablas esperadas

El dashboard espera estas tablas en el schema `main_marts`:

```text
fct_contract_prices
mart_market_snapshot
mart_contract_leaders
mart_top_movers
mart_price_trends
mart_rolling_averages
mart_candidate_momentum
mart_turning_points
mart_volatility_analysis
mart_spread_analysis
mart_anomaly_detection
```
