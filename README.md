# PredictIt Data With Airflow And Snowflake

Pipeline de ingenieria de datos para extraer informacion publica de PredictIt, almacenarla en capas raw/processed, cargarla en Snowflake, transformar los datos con dbt y visualizarlos en Power BI.

## Arquitectura

```text
PredictIt API
  -> Airflow
  -> Python extract
  -> JSON raw local: data/raw/predictit/
  -> Python transform
  -> Parquet processed local: data/processed/predictit/
  -> Snowflake RAW schema
  -> dbt Snowflake models
  -> Snowflake ANALYTICS schema
  -> Power BI
```

DuckDB se mantiene como fallback local para pruebas, pero el flujo principal del proyecto es Snowflake.

## Estructura

```text
airflow/
|-- dags/                       # DAG principal de Airflow
|-- src/                        # Extraccion, transformacion y loaders
|-- dbt/                        # Profile dbt y proyecto predictit_dbt
|-- dashboards/                 # Proyecto Power BI
|-- scripts/                    # Inicializacion de Airflow
|-- .env.example                # Plantilla de variables de entorno
|-- requirements.txt
`-- README.md
```

## Requisitos

- Python 3.10 o 3.11 recomendado para Airflow 2.9.2.
- Cuenta de Snowflake con warehouse activo.
- Permisos para crear o usar:
  - database: `PREDICTIT`
  - schema raw: `RAW`
  - schema analitico dbt: `ANALYTICS`
  - stage interno: `PREDICTIT_PARQUET_STAGE`
- Power BI Desktop si se desea abrir el dashboard.

## Instalacion

En WSL/Linux:

```bash
cd /mnt/d/final_mineria/airflow
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si `python3.11` no existe, instala Python 3.11 o usa una version compatible con Airflow 2.9.2. Evita Python 3.14 para este proyecto.

## Configuracion

Copia la plantilla:

```bash
cp .env.example .env
```

Completa tus datos reales en `.env`:

```bash
PROJECT_ROOT=/mnt/d/final_mineria/airflow
DATA_WAREHOUSE=snowflake
DBT_TARGET=snowflake
DBT_PROFILES_DIR=/mnt/d/final_mineria/airflow/dbt
DBT_BIN=/mnt/d/final_mineria/airflow/.venv/bin/dbt

SNOWFLAKE_ACCOUNT=tu_account
SNOWFLAKE_USER=tu_usuario
SNOWFLAKE_PASSWORD=tu_password
SNOWFLAKE_ROLE=tu_rol
SNOWFLAKE_WAREHOUSE=tu_warehouse
SNOWFLAKE_DATABASE=PREDICTIT
SNOWFLAKE_RAW_SCHEMA=RAW
SNOWFLAKE_SCHEMA=ANALYTICS
SNOWFLAKE_STAGE=PREDICTIT_PARQUET_STAGE
```

No subas `.env` al repositorio. Ya esta incluido en `.gitignore`.

## Ejecucion manual del pipeline

Con el entorno activado:

```bash
source .venv/bin/activate
set -a
source .env
set +a

python src/extract_predictit.py
python src/transform_to_parquet.py
python src/load_snowflake.py
cd dbt/predictit_dbt
dbt run --profiles-dir ../
dbt test --profiles-dir ../
```

## Ejecucion con Airflow

Inicializa Airflow:

```bash
source .venv/bin/activate
set -a
source .env
set +a

chmod +x scripts/init_airflow.sh
./scripts/init_airflow.sh
```

Levanta los servicios:

```bash
export AIRFLOW_HOME=$PROJECT_ROOT/airflow_home
airflow scheduler
```

En otra terminal:

```bash
source .venv/bin/activate
set -a
source .env
set +a
export AIRFLOW_HOME=$PROJECT_ROOT/airflow_home
airflow webserver --port 8080
```

Abre Airflow en `http://localhost:8080` y ejecuta el DAG:

```text
predictit_local_pipeline
```

El DAG ejecuta:

1. `extract_predictit`: descarga JSON desde PredictIt.
2. `transform_to_parquet`: genera Parquet de markets y contracts.
3. `load_warehouse`: carga a Snowflake por defecto.
4. `dbt_run`: crea vistas/tablas analiticas en Snowflake.
5. `dbt_test`: valida reglas basicas de calidad.

## Modelos dbt

Fuentes:

- `RAW.MARKETS`
- `RAW.CONTRACTS`

Modelos:

- `stg_markets`
- `stg_contracts`
- `fct_contract_prices`
- `mart_market_snapshot`
- `mart_price_trends`

Tests actuales:

- `market_id` no nulo en `stg_markets`
- `contract_id` no nulo en `stg_contracts`

## Power BI

El dashboard actual fue construido originalmente contra DuckDB por ODBC. Para la version Snowflake, conecta Power BI directamente a Snowflake y usa las tablas creadas por dbt en el schema analitico, por ejemplo:

- `ANALYTICS_MARTS.FCT_CONTRACT_PRICES`
- `ANALYTICS_MARTS.MART_MARKET_SNAPSHOT`
- `ANALYTICS_MARTS.MART_PRICE_TRENDS`

El nombre exacto del schema depende de `SNOWFLAKE_SCHEMA`. Con el valor por defecto `ANALYTICS`, dbt crea schemas derivados como `ANALYTICS_STAGING` y `ANALYTICS_MARTS`.

## Fallback local con DuckDB

Para probar sin Snowflake:

```bash
DATA_WAREHOUSE=duckdb
DBT_TARGET=duckdb
```

Luego ejecuta:

```bash
python src/run_pipeline.py
cd dbt/predictit_dbt
dbt run --profiles-dir ../ --target duckdb
dbt test --profiles-dir ../ --target duckdb
```

## Estado del proyecto

Implementado:

- Extraccion desde PredictIt API.
- Persistencia raw en JSON particionado.
- Transformacion a Parquet.
- Carga a Snowflake desde Parquet.
- Orquestacion con Airflow.
- Modelado dbt sobre Snowflake.
- Tests basicos de calidad.
- Fallback local con DuckDB.

Pendiente antes de exponer:

- Completar `.env` con credenciales reales.
- Ejecutar el DAG completo en Airflow.
- Reconectar o ajustar Power BI para leer desde Snowflake.
- Agregar capturas o evidencia de ejecucion para la presentacion final.
