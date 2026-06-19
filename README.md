# PredictIt Local Data Pipeline (Optimized for Power BI)

Proyecto principal para minería de datos e ingeniería de datos local, completamente automatizado con Apache Airflow, DuckDB y dbt, listo para visualizar en Power BI.

## Objetivo

Construir un pipeline automatizado que extrae datos desde la API pública de PredictIt, guarda una copia cruda en disco, transforma los datos a Parquet, los expone en DuckDB y ejecuta modelos analíticos con dbt. Todo el flujo es orquestado por un único DAG de Airflow.

## Arquitectura Final

```text
PredictIt API
↓
Airflow local (Orquestador 100% automatizado)
↓
Python pipeline (Extracción y Transformación inicial)
↓
Bronze: JSON crudo (`data/raw/`)
↓
Silver: Parquet procesado (`data/processed/`)
↓
Gold: DuckDB (`data/warehouse/predictit.duckdb`)
↓
dbt (Ejecutado automáticamente por Airflow)
↓
Power BI (Conexión vía ODBC a DuckDB)
```

## Estructura Optimizada

```text
predictit-data-pipeline/
├── dags/                       # DAG de Airflow (incluye tareas de dbt)
├── src/                        # Código Python del pipeline
├── data/
│   ├── raw/                    # JSON original
│   ├── processed/              # Parquet procesado
│   └── warehouse/              # Base DuckDB
├── dbt/                        # Proyecto dbt
├── dashboards/                 # Archivos de Power BI (.pbix)
├── scripts/                    # Script de inicialización de Airflow
├── requirements.txt
├── .env                        # Variables de entorno
└── README.md
```

## Instalación y Configuración Inicial (WSL/Linux)

```bash
cd predictit-data-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Instalar dbt y dependencias compatibles
pip install dbt-core==1.8.4 dbt-duckdb==1.8.2 protobuf==4.25.3
```

Edita `.env` para asegurar que `PROJECT_ROOT` apunte a la ruta absoluta de tu proyecto (ej. `/mnt/d/mineria data/airflow`).

## Orquestación con Airflow (Flujo Completo)

Hemos integrado la ejecución de dbt directamente dentro del DAG de Airflow (`predictit_local_pipeline`). El DAG ejecuta secuencialmente:
1. `extract_predictit`: Descarga JSON de la API.
2. `transform_to_parquet`: Convierte a formato Parquet.
3. `load_duckdb`: Actualiza las vistas crudas en DuckDB.
4. `dbt_run`: Ejecuta los modelos de dbt para crear las tablas analíticas (`fct_*`, `mart_*`).
5. `dbt_test`: Valida que los datos cumplan con las reglas de negocio (ej. IDs únicos, no nulos).

### Inicializar Airflow

Usa el script proporcionado para configurar Airflow automáticamente:
```bash
chmod +x scripts/init_airflow.sh
./scripts/init_airflow.sh
```

Levanta Airflow:
```bash
source .venv/bin/activate
export PROJECT_ROOT=$(pwd)
export AIRFLOW_HOME=$PROJECT_ROOT/airflow_home
export PYTHONPATH=$PROJECT_ROOT/src:$PYTHONPATH

airflow scheduler
# En otra terminal
airflow webserver --port 8080
```

## Conexión a Power BI (El Resultado Final)

Dado que Airflow automatiza toda la carga y transformación, **Power BI solo necesita conectarse a DuckDB para leer los resultados finales**.

1. **Instalación del Driver**: Descarga e instala el **DuckDB ODBC driver** para Windows.
2. **Configuración DSN**: Abre "Orígenes de datos ODBC (64 bits)" en Windows. Añade un nuevo DSN seleccionando DuckDB y en la ruta del archivo pon la ubicación local de tu base de datos:
   `D:\mineria data\airflow\data\warehouse\predictit.duckdb`
3. **Importación**: En Power BI Desktop, selecciona **Obtener Datos -> ODBC**, selecciona tu DSN y carga las tablas de la capa `marts` (ej. `main_marts.mart_market_snapshot`).

> **Nota Alternativa:** Si prefieres no usar ODBC, Power BI puede leer directamente los archivos Parquet en la carpeta `data/processed/predictit/`.

## Buenas prácticas aplicadas
- Orquestación centralizada (Extracción + Transformación DWH) en un solo DAG de Airflow.
- Separación entre Bronze (raw), Silver (processed) y Gold (warehouse).
- Particiones de datos por fecha y hora.
- Testing automatizado con dbt.
- Pipeline local sin costos de nube, pero estructurado para migración directa a AWS S3 y Snowflake.
