# Dashboards de Power BI (PBIP)

Esta carpeta contiene el proyecto de Power BI estructurado como Power BI Project (`.pbip`).

## Contenido

* **`airflowx.pbip`**: archivo de proyecto principal de Power BI.
* **`airflowx.SemanticModel/`**: definicion del modelo de datos en TMDL.
* **`airflowx.Report/`**: definicion visual del dashboard en JSON.

## Visualizaciones incluidas

El reporte contiene dos paginas de analisis de mercados de prediccion de PredictIt:

1. **Overview**: KPI principales, distribucion de probabilidades, contratos por mercado y variacion de precios.
2. **Analisis de Precios**: analisis temporal y dispersion entre precio actual y variacion.

## Consideraciones tecnicas

* El dashboard fue creado inicialmente leyendo `predictit.duckdb` via ODBC.
* Para la entrega con Snowflake, reconecta el modelo semantico a Snowflake y usa las tablas creadas por dbt en el schema de marts.
* Con `SNOWFLAKE_SCHEMA=ANALYTICS`, dbt crea tablas en schemas como `ANALYTICS_MARTS`.
* Cualquier ajuste de diseno debe realizarse desde Power BI Desktop. Editar `page.json` manualmente puede producir errores de esquema.
