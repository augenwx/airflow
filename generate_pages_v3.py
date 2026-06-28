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

# ================= PAGE 1 =================
page1_id = "1f83ed0981004ac1bcca"
clean_visuals(page1_id)

def wrap_visual(name, x, y, w, h, z, visual_type, query_obj, objects_obj=None):
    base = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": query_obj},
            "drillFilterOtherVisuals": True
        }
    }
    if objects_obj:
        base["visual"]["objects"] = objects_obj
    return json.dumps(base, indent=2)

visuals_p1 = {}

# Slicer Market
visuals_p1["slicer_market"] = wrap_visual("slicer_market", 700, 10, 250, 60, 1, "slicer",
    {"Values": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_market"}}, "Property": "market_name"}}, "queryRef": "dim_market.market_name", "nativeQueryRef": "Market", "active": True}]}},
    {"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}]}
)

# Slicer Contract
visuals_p1["slicer_contract"] = wrap_visual("slicer_contract", 970, 10, 250, 60, 2, "slicer",
    {"Values": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_contract"}}, "Property": "contract_name"}}, "queryRef": "dim_contract.contract_name", "nativeQueryRef": "Contract", "active": True}]}},
    {"data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}]}
)

# KPI Cards (Row 1)
# 1. Total Markets Historical
visuals_p1["kpi_markets"] = wrap_visual("kpi_markets", 160, 80, 170, 90, 3, "card",
    {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Total Markets Historical"}}, "queryRef": "fct_contract_prices.Total Markets Historical", "nativeQueryRef": "Total Markets"}]}})

# 2. Total Contracts Active
visuals_p1["kpi_contracts"] = wrap_visual("kpi_contracts", 340, 80, 170, 90, 4, "card",
    {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "Total Contracts Active"}}, "queryRef": "mart_market_snapshot.Total Contracts Active", "nativeQueryRef": "Total Contracts"}]}})

# 3. Avg Price
visuals_p1["kpi_avg_price"] = wrap_visual("kpi_avg_price", 520, 80, 170, 90, 5, "card",
    {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "Precio Promedio Actual"}}, "queryRef": "mart_market_snapshot.Precio Promedio Actual", "nativeQueryRef": "Precio Promedio"}]}})

# 4. Top Gainer
visuals_p1["kpi_gainer"] = wrap_visual("kpi_gainer", 700, 80, 170, 90, 6, "card",
    {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "Mayor Gainer 24h"}}, "queryRef": "mart_top_movers.Mayor Gainer 24h", "nativeQueryRef": "Mayor Gainer"}]}})

# 5. Top Loser
visuals_p1["kpi_loser"] = wrap_visual("kpi_loser", 880, 80, 170, 90, 7, "card",
    {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "Mayor Loser 24h"}}, "queryRef": "mart_top_movers.Mayor Loser 24h", "nativeQueryRef": "Mayor Loser"}]}})

# 6. Anomalies
visuals_p1["kpi_anomalies"] = wrap_visual("kpi_anomalies", 1060, 80, 170, 90, 8, "card",
    {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "Anomalías Activas"}}, "queryRef": "mart_anomaly_detection.Anomalías Activas", "nativeQueryRef": "Anomalías Activas"}]}})

# Row 2
# Top Movers (Table)
visuals_p1["table_movers"] = wrap_visual("table_movers", 160, 180, 360, 250, 9, "tableEx",
    {"Values": {"projections": [
        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "contract_name"}}, "queryRef": "mart_top_movers.contract_name", "nativeQueryRef": "Contrato"},
        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_market"}}, "Property": "market_name"}}, "queryRef": "dim_market.market_name", "nativeQueryRef": "Mercado"},
        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "Precio Actual"}}, "queryRef": "mart_top_movers.Precio Actual", "nativeQueryRef": "Precio Actual"},
        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "Cambio 24h"}}, "queryRef": "mart_top_movers.Cambio 24h", "nativeQueryRef": "Cambio %"}
    ]}})

# Leaders (Bar Chart)
visuals_p1["bar_leaders"] = wrap_visual("bar_leaders", 530, 180, 360, 250, 10, "barChart",
    {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_contract_leaders"}}, "Property": "contract_name"}}, "queryRef": "mart_contract_leaders.contract_name", "nativeQueryRef": "Contrato", "active": True}]},
        "Y": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_contract_leaders"}}, "Property": "Leader Price"}}, "queryRef": "mart_contract_leaders.Leader Price", "nativeQueryRef": "Leader Price"}]}
    },
    {"legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]}
)

# Distribution (Donut Chart)
visuals_p1["donut_dist"] = wrap_visual("donut_dist", 900, 180, 360, 250, 11, "donutChart",
    {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_market"}}, "Property": "market_name"}}, "queryRef": "dim_market.market_name", "nativeQueryRef": "Mercado", "active": True}]},
        "Y": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "Total Contracts Active"}}, "queryRef": "mart_market_snapshot.Total Contracts Active", "nativeQueryRef": "Contratos"}]}
    }
)

# Row 3
# Snapshot (Table)
visuals_p1["table_snapshot"] = wrap_visual("table_snapshot", 160, 440, 360, 270, 12, "tableEx",
    {"Values": {"projections": [
        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_market"}}, "Property": "market_name"}}, "queryRef": "dim_market.market_name", "nativeQueryRef": "Mercado"},
        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "Total Contracts Active"}}, "queryRef": "mart_market_snapshot.Total Contracts Active", "nativeQueryRef": "Contratos"},
        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "Precio Promedio Actual"}}, "queryRef": "mart_market_snapshot.Precio Promedio Actual", "nativeQueryRef": "Precio Promedio"},
        {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "Spread Promedio Yes"}}, "queryRef": "mart_market_snapshot.Spread Promedio Yes", "nativeQueryRef": "Spread"}
    ]}})

# Anomalies (Table)
visuals_p1["table_anomalies"] = wrap_visual("table_anomalies", 530, 440, 360, 270, 13, "tableEx",
    {"Values": {"projections": [
        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "contract_name"}}, "queryRef": "mart_anomaly_detection.contract_name", "nativeQueryRef": "Contrato"},
        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "dim_market"}}, "Property": "market_name"}}, "queryRef": "dim_market.market_name", "nativeQueryRef": "Mercado"},
        {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "z_score"}}, "queryRef": "mart_anomaly_detection.z_score", "nativeQueryRef": "Z-Score"}
    ]}})

# Spreads (Column Chart)
visuals_p1["column_spreads"] = wrap_visual("column_spreads", 900, 440, 360, 270, 14, "columnChart",
    {
        "Category": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "contract_name"}}, "queryRef": "mart_spread_analysis.contract_name", "nativeQueryRef": "Contrato", "active": True}]},
        "Y": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "Avg Market Spread"}}, "queryRef": "mart_spread_analysis.Avg Market Spread", "nativeQueryRef": "Spread Promedio"}]}
    },
    {"legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]}
)

# Write all visuals
for name, json_str in visuals_p1.items():
    write_raw_json(os.path.join(BASE_PATH, page1_id, "visuals", name, "visual.json"), json_str)

print("V3 Premium Layout generated!")
