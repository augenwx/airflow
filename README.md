# PredictIt Local Data Pipeline

Proyecto principal para minería de datos e ingeniería de datos local.

## Objetivo

Construir un pipeline automatizado que extrae datos desde la API pública de PredictIt, guarda una copia cruda en disco, transforma los datos a Parquet, los expone en DuckDB y permite crear modelos analíticos con dbt.

Arquitectura:

```text
PredictIt API
↓
Airflow local
↓
Python pipeline
↓
Bronze: JSON crudo
↓
Silver: Parquet procesado
↓
DuckDB
↓
dbt
↓
Gold: tablas analíticas
↓
Power BI
```

## Estructura

```text
predictit-data-pipeline/
├── dags/                       # DAG de Airflow
├── src/                        # Código Python del pipeline
├── data/
│   ├── raw/                    # JSON original
│   ├── processed/              # Parquet procesado
│   └── warehouse/              # Base DuckDB
├── dbt/                        # Proyecto dbt
├── notebooks/                  # Exploración y minería de datos
├── dashboards/                 # Dashboards
├── scripts/                    # Scripts de ejecución local
├── requirements.txt
└── README.md
```

## Instalación local

```bash
cd predictit-data-pipeline
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` si necesitas cambiar rutas.

## Ejecutar sin Airflow

```bash
bash scripts/run_local_pipeline.sh
```

Esto hace tres pasos:

1. Descarga JSON desde PredictIt.
2. Convierte mercados y contratos a Parquet.
3. Crea/actualiza vistas en DuckDB.

## Ejecutar consultas en DuckDB

```bash
duckdb data/warehouse/predictit.duckdb
```

Ejemplo:

```sql
SELECT * FROM analytics.market_contract_prices LIMIT 10;
```

## Ejecutar con Airflow local

Define la ruta del proyecto:

```bash
export PROJECT_ROOT=/ruta/absoluta/predictit-data-pipeline
export AIRFLOW_HOME=$PROJECT_ROOT/airflow_home
export PYTHONPATH=$PROJECT_ROOT/src:$PYTHONPATH
```

Inicializa Airflow:

```bash
airflow db migrate
airflow users create \
  --username admin \
  --firstname Miguel \
  --lastname Data \
  --role Admin \
  --email admin@example.com \
  --password admin
```

Copia o enlaza el DAG:

```bash
mkdir -p $AIRFLOW_HOME/dags
ln -s $PROJECT_ROOT/dags/predictit_dag.py $AIRFLOW_HOME/dags/predictit_dag.py
```

Levanta Airflow:

```bash
airflow scheduler
# en otra terminal
airflow webserver --port 8080
```

DAG: `predictit_local_pipeline`.

## Ejecutar dbt con DuckDB

Desde la carpeta `dbt`:

```bash
cd dbt
mkdir -p ~/.dbt
cp profiles.yml.example ~/.dbt/profiles.yml
cd predictit_dbt
dbt debug
dbt run
dbt test
```

Modelos incluidos:

- `stg_markets`: limpia datos de mercados.
- `stg_contracts`: limpia datos de contratos.
- `fct_contract_prices`: tabla histórica de precios.
- `mart_market_snapshot`: último snapshot disponible.
- `mart_price_trends`: tendencias por hora.

## Preguntas de minería de datos sugeridas

- ¿Qué contratos tienen mayor variación de precio?
- ¿Qué mercados cambian más rápido por hora o por día?
- ¿Hay contratos con tendencia ascendente o descendente persistente?
- ¿Qué señales aparecen antes de cambios fuertes de precio?
- ¿Se puede predecir el próximo movimiento usando datos históricos?

## Buenas prácticas aplicadas

- Separación entre raw, processed y warehouse.
- Particiones por fecha y hora.
- Datos raw preservados sin alterar.
- Transformaciones separadas en dbt.
- Orquestación con Airflow.
- Reemplazo económico de S3/Snowflake usando disco local y DuckDB.

## Nota

El endpoint configurado por defecto es:

```text
https://www.predictit.org/api/marketdata/all/
```

Si PredictIt cambia la API, actualiza `PREDICTIT_API_URL` en `.env`.
# airflow
"# airflow" 
