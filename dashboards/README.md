# Dashboards de Power BI (PBIP)

Esta carpeta contiene el proyecto de Power BI estructurado como **Power BI Project (.pbip)**.

Al usar PBIP, en lugar de un archivo binario `.pbix` opaco, todo el modelo de datos y las visualizaciones se guardan en archivos de texto plano legibles, lo que permite un control de versiones adecuado mediante Git.

## Contenido

*   **`airflowx.pbip`**: El archivo de proyecto principal de Power BI. Ábrelo con Power BI Desktop.
*   **`airflowx.SemanticModel/`**: Contiene la definición del modelo de datos usando el formato TMDL (Tabular Model Definition Language). Aquí se encuentran las medidas DAX (ej. en `fct_contract_prices.tmdl`).
*   **`airflowx.Report/`**: Contiene la definición visual del dashboard en formato JSON. Incluye las páginas y los visuales nativos.

## Visualizaciones Incluidas

El reporte **PredictIt Analytics Dashboard** contiene cuatro páginas de análisis de los mercados de predicción de PredictIt:

1.  **Executive Overview**: KPI principales, líderes, movimientos 24h, snapshot de mercado y anomalías.
2.  **Historical Trends**: evolución histórica, momentum, promedios móviles y puntos de giro.
3.  **Risk & Anomalies**: señales estadísticas, spreads, volatilidad y mapa de riesgo.
4.  **Contract Detail**: detalle por contrato para drill-through con precio, promedios móviles, contexto de mercado y microestructura.

## Consideraciones Técnicas

*   El modelo de datos lee directamente de `predictit.duckdb` vía ODBC usando el DSN `duckdb2` y el esquema `main_marts`.
*   El modelo incluye dimensiones compartidas `dim_market`, `dim_contract` y `dim_date` para filtrar los marts sin relaciones many-to-many directas.
*   Asegúrate de que la carga paralela ("Parallel loading of tables") esté deshabilitada en la configuración global de Power BI Desktop para evitar bloqueos del archivo de base de datos DuckDB al recargar.
*   Cualquier ajuste de diseño (colores, fondos, estilo) debe realizarse a través de la interfaz de Power BI Desktop. Editar el archivo `page.json` manualmente puede resultar en errores de esquema.
