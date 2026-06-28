import os
import json
import shutil

BASE_PATH = r"D:\mineria data\airflow\dashboards\airflowx.Report\definition\pages"

def write_raw_json(path, raw_json_str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(raw_json_str)

def clean_visuals(page_id):
    visuals_dir = os.path.join(BASE_PATH, page_id, "visuals")
    if os.path.exists(visuals_dir):
        shutil.rmtree(visuals_dir)

# pages.json remains same
pages_json = """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
  "pageOrder": [
    "1f83ed0981004ac1bcca",
    "a2b3c4d5e6f7a8b9c0d1",
    "b3c4d5e6f7a8b9c0d1e2"
  ],
  "activePageName": "1f83ed0981004ac1bcca"
}"""
write_raw_json(os.path.join(BASE_PATH, "pages.json"), pages_json)

# Slicer template
def get_slicer_json(name, entity):
    return """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": \"""" + name + """\",
  "position": {"x": 10, "y": 10, "z": 0, "height": 80, "width": 1260, "tabOrder": 0},
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": \"""" + entity + """\"}}, "Property": "market_name"}},
              "queryRef": \"""" + entity + """.market_name\",
              "nativeQueryRef": "Selecciona el Mercado (Pregunta)",
              "active": true
            }
          ]
        }
      }
    },
    "objects": {
      "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
      "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}"""

# ================= PAGE 1 =================
page1_id = "1f83ed0981004ac1bcca"
clean_visuals(page1_id)
write_raw_json(os.path.join(BASE_PATH, page1_id, "page.json"), """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
  "name": "1f83ed0981004ac1bcca",
  "displayName": "1. Executive Overview",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280
}""")

visuals_p1 = {
    "slicer_market_top": get_slicer_json("slicer_market_top", "mart_market_snapshot"),
    "card_total_contracts": """{
  "name": "card_total_contracts",
  "position": {"x": 10, "y": 100, "z": 1, "height": 100, "width": 400, "tabOrder": 1},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Total Contracts"}}, "queryRef": "fct_contract_prices.Total Contracts", "nativeQueryRef": "Total de Contratos"}]}}},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_top_gainer": """{
  "name": "card_top_gainer",
  "position": {"x": 430, "y": 100, "z": 2, "height": 100, "width": 400, "tabOrder": 2},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "Top Gainer Name"}}, "queryRef": "mart_top_movers.Top Gainer Name", "nativeQueryRef": "Mayor Subida (24H)"}]}}},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_last_updated": """{
  "name": "card_last_updated",
  "position": {"x": 850, "y": 100, "z": 3, "height": 100, "width": 420, "tabOrder": 3},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Max Trade Price"}}, "queryRef": "fct_contract_prices.Max Trade Price", "nativeQueryRef": "Última Actualización"}]}}},
    "drillFilterOtherVisuals": true
  }
}""",
    "bar_leaders": """{
  "name": "bar_leaders",
  "position": {"x": 10, "y": 210, "z": 4, "height": 500, "width": 610, "tabOrder": 4},
  "visual": {
    "visualType": "barChart",
    "query": {
      "queryState": {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_contract_leaders"}}, "Property": "contract_name"}}, "queryRef": "mart_contract_leaders.contract_name", "nativeQueryRef": "Candidato", "active": true}]},
        "Y": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_contract_leaders"}}, "Property": "Leader Price"}}, "queryRef": "mart_contract_leaders.Leader Price", "nativeQueryRef": "Precio Actual / Probabilidad"}]}
      }
    },
    "objects": {"legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "bar_movers": """{
  "name": "bar_movers",
  "position": {"x": 640, "y": 210, "z": 5, "height": 240, "width": 630, "tabOrder": 5},
  "visual": {
    "visualType": "barChart",
    "query": {
      "queryState": {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "contract_name"}}, "queryRef": "mart_top_movers.contract_name", "nativeQueryRef": "Candidato", "active": true}]},
        "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "change_pct"}}, "queryRef": "mart_top_movers.change_pct", "nativeQueryRef": "Cambio en 24H (%)"}]}
      }
    },
    "objects": {"legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "line_overview": """{
  "name": "line_overview",
  "position": {"x": 640, "y": 460, "z": 6, "height": 250, "width": 630, "tabOrder": 6},
  "visual": {
    "visualType": "lineChart",
    "query": {
      "queryState": {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "snapshot_hour"}}, "queryRef": "mart_price_trends.snapshot_hour", "nativeQueryRef": "Hora", "active": true}]},
        "Series": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "contract_name"}}, "queryRef": "mart_price_trends.contract_name", "nativeQueryRef": "Candidato"}]},
        "Y": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "Trend Avg Price"}}, "queryRef": "mart_price_trends.Trend Avg Price", "nativeQueryRef": "Precio Promedio"}]}
      }
    },
    "drillFilterOtherVisuals": true
  }
}"""
}

for k in visuals_p1:
    if k != "slicer_market_top":
        visuals_p1[k] = """{ "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json", """ + visuals_p1[k][1:]

for name, json_str in visuals_p1.items():
    write_raw_json(os.path.join(BASE_PATH, page1_id, "visuals", name, "visual.json"), json_str)


# ================= PAGE 2 =================
page2_id = "a2b3c4d5e6f7a8b9c0d1"
clean_visuals(page2_id)
write_raw_json(os.path.join(BASE_PATH, page2_id, "page.json"), """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
  "name": "a2b3c4d5e6f7a8b9c0d1",
  "displayName": "2. Historical Trends",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280
}""")

visuals_p2 = {
    "slicer_market_top": get_slicer_json("slicer_market_top", "mart_price_trends"),
    "line_rolling_avg": """{
  "name": "line_rolling_avg",
  "position": {"x": 10, "y": 100, "z": 1, "height": 300, "width": 800, "tabOrder": 1},
  "visual": {
    "visualType": "lineChart",
    "query": {
      "queryState": {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_rolling_averages"}}, "Property": "snapshot_date"}}, "queryRef": "mart_rolling_averages.snapshot_date", "nativeQueryRef": "Fecha", "active": true}]},
        "Series": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_rolling_averages"}}, "Property": "contract_name"}}, "queryRef": "mart_rolling_averages.contract_name", "nativeQueryRef": "Candidato"}]},
        "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_rolling_averages"}}, "Property": "avg_7d"}}, "queryRef": "mart_rolling_averages.avg_7d", "nativeQueryRef": "Promedio Móvil 7D"}]}
      }
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "scatter_momentum": """{
  "name": "scatter_momentum",
  "position": {"x": 820, "y": 100, "z": 2, "height": 300, "width": 450, "tabOrder": 2},
  "visual": {
    "visualType": "scatterChart",
    "query": {
      "queryState": {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "contract_name"}}, "queryRef": "mart_candidate_momentum.contract_name", "nativeQueryRef": "Candidato", "active": true}]},
        "X": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "avg_daily_change"}}, "queryRef": "mart_candidate_momentum.avg_daily_change", "nativeQueryRef": "Velocidad de Subida (Momentum)", "active": true}]},
        "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "current_price"}}, "queryRef": "mart_candidate_momentum.current_price", "nativeQueryRef": "Precio Actual"}]}
      }
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "table_turning_points": """{
  "name": "table_turning_points",
  "position": {"x": 10, "y": 410, "z": 3, "height": 300, "width": 1260, "tabOrder": 3},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "snapshot_date"}}, "queryRef": "mart_turning_points.snapshot_date", "nativeQueryRef": "Fecha"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "contract_name"}}, "queryRef": "mart_turning_points.contract_name", "nativeQueryRef": "Candidato"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "impact"}}, "queryRef": "mart_turning_points.impact", "nativeQueryRef": "Impacto Numérico"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "trend_direction"}}, "queryRef": "mart_turning_points.trend_direction", "nativeQueryRef": "Cambio de Tendencia"}
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}"""
}

for k in visuals_p2:
    if k != "slicer_market_top":
        visuals_p2[k] = """{ "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json", """ + visuals_p2[k][1:]

for name, json_str in visuals_p2.items():
    write_raw_json(os.path.join(BASE_PATH, page2_id, "visuals", name, "visual.json"), json_str)


# ================= PAGE 3 =================
page3_id = "b3c4d5e6f7a8b9c0d1e2"
clean_visuals(page3_id)
write_raw_json(os.path.join(BASE_PATH, page3_id, "page.json"), """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
  "name": "b3c4d5e6f7a8b9c0d1e2",
  "displayName": "3. Data Mining & Volatility",
  "displayOption": "FitToPage",
  "height": 720,
  "width": 1280
}""")

visuals_p3 = {
    "slicer_market_top": get_slicer_json("slicer_market_top", "mart_volatility_analysis"),
    "scatter_spread": """{
  "name": "scatter_spread",
  "position": {"x": 10, "y": 100, "z": 1, "height": 610, "width": 620, "tabOrder": 1},
  "visual": {
    "visualType": "scatterChart",
    "query": {
      "queryState": {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "contract_name"}}, "queryRef": "mart_spread_analysis.contract_name", "nativeQueryRef": "Candidato", "active": true}]},
        "X": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "current_spread_yes"}}, "queryRef": "mart_spread_analysis.current_spread_yes", "nativeQueryRef": "Spread Actual (Iliquidez)", "active": true}]},
        "Y": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "implied_volatility"}}, "queryRef": "mart_spread_analysis.implied_volatility", "nativeQueryRef": "Volatilidad Implícita"}]}
      }
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "matrix_anomalies": """{
  "name": "matrix_anomalies",
  "position": {"x": 640, "y": 100, "z": 2, "height": 610, "width": 630, "tabOrder": 2},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "contract_name"}}, "queryRef": "mart_anomaly_detection.contract_name", "nativeQueryRef": "Candidato"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "current_price"}}, "queryRef": "mart_anomaly_detection.current_price", "nativeQueryRef": "Precio Actual"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "signal_type"}}, "queryRef": "mart_anomaly_detection.signal_type", "nativeQueryRef": "Tipo de Alarma / Señal"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "is_anomaly"}}, "queryRef": "mart_anomaly_detection.is_anomaly", "nativeQueryRef": "¿Es Anomalía?"}
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}"""
}

for k in visuals_p3:
    if k != "slicer_market_top":
        visuals_p3[k] = """{ "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json", """ + visuals_p3[k][1:]

for name, json_str in visuals_p3.items():
    write_raw_json(os.path.join(BASE_PATH, page3_id, "visuals", name, "visual.json"), json_str)

print("Redesign complete! Generated new visual layout.")
