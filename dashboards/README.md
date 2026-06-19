# Dashboards de Power BI (PBIP)

Esta carpeta contiene el proyecto de Power BI estructurado como **Power BI Project (.pbip)**.

Al usar PBIP, en lugar de un archivo binario `.pbix` opaco, todo el modelo de datos y las visualizaciones se guardan en archivos de texto plano legibles, lo que permite un control de versiones adecuado mediante Git.

## Contenido

*   **`airflowx.pbip`**: El archivo de proyecto principal de Power BI. Ábrelo con Power BI Desktop.
*   **`airflowx.SemanticModel/`**: Contiene la definición del modelo de datos usando el formato TMDL (Tabular Model Definition Language). Aquí se encuentran las medidas DAX (ej. en `fct_contract_prices.tmdl`).
*   **`airflowx.Report/`**: Contiene la definición visual del dashboard en formato JSON. Incluye las páginas y los visuales nativos.

## Visualizaciones Incluidas

El reporte contiene dos páginas de análisis de los mercados de predicción de PredictIt:

1.  **Overview**: KPI principales, distribución de probabilidades, contratos por mercado y variación de precios.
2.  **Análisis de Precios**: Análisis en el tiempo (gráficos de líneas) y un gráfico de dispersión cruzando el precio actual vs. su variación (ganadores/perdedores).

## Consideraciones Técnicas

*   El modelo de datos lee directamente de `predictit.duckdb` vía ODBC.
*   Asegúrate de que la carga paralela ("Parallel loading of tables") esté deshabilitada en la configuración global de Power BI Desktop para evitar bloqueos del archivo de base de datos DuckDB al recargar.
*   Cualquier ajuste de diseño (colores, fondos, estilo) debe realizarse a través de la interfaz de Power BI Desktop. Editar el archivo `page.json` manualmente puede resultar en errores de esquema.
