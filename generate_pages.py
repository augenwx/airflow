import os
import json
import shutil

BASE_PATH = r"D:\mineria data\airflow\dashboards\airflowx.Report\definition\pages"

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def write_raw_json(path, raw_json_str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(raw_json_str)

def clean_visuals(page_id):
    visuals_dir = os.path.join(BASE_PATH, page_id, "visuals")
    if os.path.exists(visuals_dir):
        shutil.rmtree(visuals_dir)

# pages.json
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

# Page 1
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
    "slicer_market": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "slicer_market",
  "position": {"x": 10, "y": 10, "z": 0, "height": 100, "width": 220, "tabOrder": 0},
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "market_name"}},
              "queryRef": "mart_market_snapshot.market_name",
              "nativeQueryRef": "Market",
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
}""",
    "card_total_markets": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_total_markets",
  "position": {"x": 240, "y": 10, "z": 1, "height": 100, "width": 190, "tabOrder": 1},
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "Total Active Markets"}},
              "queryRef": "mart_market_snapshot.Total Active Markets",
              "nativeQueryRef": "Total Markets"
            }
          ]
        }
      }
    },
    "objects": {
      "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "28D"}}}}}],
      "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "card_total_contracts": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_total_contracts",
  "position": {"x": 440, "y": 10, "z": 2, "height": 100, "width": 190, "tabOrder": 2},
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Total Contracts"}},
              "queryRef": "fct_contract_prices.Total Contracts",
              "nativeQueryRef": "Total Contracts"
            }
          ]
        }
      }
    },
    "objects": {
      "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "28D"}}}}}],
      "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "card_top_gainer": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_top_gainer",
  "position": {"x": 640, "y": 10, "z": 3, "height": 100, "width": 190, "tabOrder": 3},
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "Top Gainer Name"}},
              "queryRef": "mart_top_movers.Top Gainer Name",
              "nativeQueryRef": "Top Gainer 24H"
            }
          ]
        }
      }
    },
    "objects": {
      "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "20D"}}}}}],
      "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "card_avg_spread": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_avg_spread",
  "position": {"x": 840, "y": 10, "z": 4, "height": 100, "width": 190, "tabOrder": 4},
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Avg Trade Price"}},
              "queryRef": "fct_contract_prices.Avg Trade Price",
              "nativeQueryRef": "Avg Price"
            }
          ]
        }
      }
    },
    "objects": {
      "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "28D"}}}}}],
      "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "card_last_updated": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_last_updated",
  "position": {"x": 1040, "y": 10, "z": 5, "height": 100, "width": 230, "tabOrder": 5},
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Max Trade Price"}},
              "queryRef": "fct_contract_prices.Max Trade Price",
              "nativeQueryRef": "Last Updated"
            }
          ]
        }
      }
    },
    "objects": {
      "labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "18D"}}}}}],
      "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "bar_leaders": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "bar_leaders",
  "position": {"x": 10, "y": 120, "z": 6, "height": 280, "width": 620, "tabOrder": 6},
  "visual": {
    "visualType": "barChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_contract_leaders"}}, "Property": "contract_name"}},
              "queryRef": "mart_contract_leaders.contract_name",
              "nativeQueryRef": "Contract",
              "active": true
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_contract_leaders"}}, "Property": "Leader Price"}},
              "queryRef": "mart_contract_leaders.Leader Price",
              "nativeQueryRef": "Price / Probability"
            }
          ]
        }
      }
    },
    "objects": {
      "dataPoint": [{"properties": {"fill": {"solid": {}}}}],
      "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "line_overview": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "line_overview",
  "position": {"x": 640, "y": 120, "z": 7, "height": 280, "width": 630, "tabOrder": 7},
  "visual": {
    "visualType": "lineChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "snapshot_hour"}},
              "queryRef": "mart_price_trends.snapshot_hour",
              "nativeQueryRef": "Time",
              "active": true
            }
          ]
        },
        "Y": {
          "projections": [
            {
              "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "Trend Avg Price"}},
              "queryRef": "mart_price_trends.Trend Avg Price",
              "nativeQueryRef": "Avg Price"
            }
          ]
        }
      }
    },
    "objects": {
      "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "table_movers": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "table_movers",
  "position": {"x": 10, "y": 410, "z": 8, "height": 300, "width": 620, "tabOrder": 8},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "contract_name"}},
              "queryRef": "mart_top_movers.contract_name",
              "nativeQueryRef": "Contract"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "market_name"}},
              "queryRef": "mart_top_movers.market_name",
              "nativeQueryRef": "Market"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "price_now"}},
              "queryRef": "mart_top_movers.price_now",
              "nativeQueryRef": "Price Now"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "change_abs"}},
              "queryRef": "mart_top_movers.change_abs",
              "nativeQueryRef": "Change 24H"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "change_pct"}},
              "queryRef": "mart_top_movers.change_pct",
              "nativeQueryRef": "Change %"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_top_movers"}}, "Property": "direction"}},
              "queryRef": "mart_top_movers.direction",
              "nativeQueryRef": "Direction"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "table_summary": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "table_summary",
  "position": {"x": 640, "y": 410, "z": 9, "height": 300, "width": 630, "tabOrder": 9},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "market_name"}},
              "queryRef": "mart_market_snapshot.market_name",
              "nativeQueryRef": "Market"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "contract_name"}},
              "queryRef": "mart_market_snapshot.contract_name",
              "nativeQueryRef": "Contract"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "last_trade_price"}},
              "queryRef": "mart_market_snapshot.last_trade_price",
              "nativeQueryRef": "Price"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "price_change_from_last_close"}},
              "queryRef": "mart_market_snapshot.price_change_from_last_close",
              "nativeQueryRef": "Change"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "spread_yes"}},
              "queryRef": "mart_market_snapshot.spread_yes",
              "nativeQueryRef": "Spread"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_market_snapshot"}}, "Property": "extraction_ts"}},
              "queryRef": "mart_market_snapshot.extraction_ts",
              "nativeQueryRef": "Timestamp"
            }
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}"""
}

for name, json_str in visuals_p1.items():
    write_raw_json(os.path.join(BASE_PATH, page1_id, "visuals", name, "visual.json"), json_str)


# Page 2
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
    "slicer_market": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "slicer_market",
  "position": {"x": 10, "y": 110, "z": 0, "height": 80, "width": 200, "tabOrder": 0},
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "market_name"}},
            "queryRef": "mart_price_trends.market_name",
            "nativeQueryRef": "Select Market",
            "active": true
          }]
        }
      }
    },
    "objects": {
      "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
      "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "slicer_candidates": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "slicer_candidates",
  "position": {"x": 10, "y": 200, "z": 1, "height": 230, "width": 200, "tabOrder": 1},
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "contract_name"}},
            "queryRef": "mart_price_trends.contract_name",
            "nativeQueryRef": "Compare Candidates",
            "active": true
          }]
        }
      }
    },
    "objects": {
      "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'List'"}}}}}],
      "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "slicer_date": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "slicer_date",
  "position": {"x": 10, "y": 440, "z": 2, "height": 80, "width": 200, "tabOrder": 2},
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "snapshot_date"}},
            "queryRef": "mart_price_trends.snapshot_date",
            "nativeQueryRef": "Date Range",
            "active": true
          }]
        }
      }
    },
    "objects": {
      "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "card_avg_change": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_avg_change",
  "position": {"x": 10, "y": 10, "z": 3, "height": 90, "width": 250, "tabOrder": 3},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "Avg Momentum"}}, "queryRef": "mart_candidate_momentum.Avg Momentum", "nativeQueryRef": "30D Avg Change"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_momentum_leader": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_momentum_leader",
  "position": {"x": 270, "y": 10, "z": 4, "height": 90, "width": 250, "tabOrder": 4},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Max Trade Price"}}, "queryRef": "fct_contract_prices.Max Trade Price", "nativeQueryRef": "Highest Momentum"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_7d_swing": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_7d_swing",
  "position": {"x": 530, "y": 10, "z": 5, "height": 90, "width": 250, "tabOrder": 5},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "fct_contract_prices"}}, "Property": "Avg Price Change"}}, "queryRef": "fct_contract_prices.Avg Price Change", "nativeQueryRef": "Largest 7D Swing"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_stability": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_stability",
  "position": {"x": 790, "y": 10, "z": 6, "height": 90, "width": 250, "tabOrder": 6},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "Trend Avg Price"}}, "queryRef": "mart_price_trends.Trend Avg Price", "nativeQueryRef": "Trend Stability"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "line_historical": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "line_historical",
  "position": {"x": 220, "y": 110, "z": 7, "height": 290, "width": 660, "tabOrder": 7},
  "visual": {
    "visualType": "lineChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "snapshot_hour"}},
            "queryRef": "mart_price_trends.snapshot_hour",
            "nativeQueryRef": "Time",
            "active": true
          }]
        },
        "Y": {
          "projections": [{
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_price_trends"}}, "Property": "Trend Avg Price"}},
            "queryRef": "mart_price_trends.Trend Avg Price",
            "nativeQueryRef": "Probability (%)"
          }]
        }
      }
    },
    "objects": {
      "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "line_rolling_avg": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "line_rolling_avg",
  "position": {"x": 220, "y": 410, "z": 8, "height": 300, "width": 660, "tabOrder": 8},
  "visual": {
    "visualType": "lineChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_rolling_averages"}}, "Property": "snapshot_date"}},
            "queryRef": "mart_rolling_averages.snapshot_date",
            "nativeQueryRef": "Date",
            "active": true
          }]
        },
        "Y": {
          "projections": [
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_rolling_averages"}}, "Property": "avg_7d"}},
              "queryRef": "mart_rolling_averages.avg_7d",
              "nativeQueryRef": "7D Avg"
            },
            {
              "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_rolling_averages"}}, "Property": "avg_30d"}},
              "queryRef": "mart_rolling_averages.avg_30d",
              "nativeQueryRef": "30D Avg"
            }
          ]
        }
      }
    },
    "objects": {
      "legend": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "table_momentum": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "table_momentum",
  "position": {"x": 890, "y": 110, "z": 9, "height": 290, "width": 380, "tabOrder": 9},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "momentum_rank"}}, "queryRef": "mart_candidate_momentum.momentum_rank", "nativeQueryRef": "Rank"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "contract_name"}}, "queryRef": "mart_candidate_momentum.contract_name", "nativeQueryRef": "Candidate"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "avg_daily_change"}}, "queryRef": "mart_candidate_momentum.avg_daily_change", "nativeQueryRef": "Avg Daily Change"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_candidate_momentum"}}, "Property": "momentum_direction"}}, "queryRef": "mart_candidate_momentum.momentum_direction", "nativeQueryRef": "Momentum"}
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "table_turning_points": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "table_turning_points",
  "position": {"x": 890, "y": 410, "z": 10, "height": 300, "width": 380, "tabOrder": 10},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "snapshot_date"}}, "queryRef": "mart_turning_points.snapshot_date", "nativeQueryRef": "Date"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "contract_name"}}, "queryRef": "mart_turning_points.contract_name", "nativeQueryRef": "Contract"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "impact"}}, "queryRef": "mart_turning_points.impact", "nativeQueryRef": "Impact"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_turning_points"}}, "Property": "trend_direction"}}, "queryRef": "mart_turning_points.trend_direction", "nativeQueryRef": "Trend"}
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}"""
}

for name, json_str in visuals_p2.items():
    write_raw_json(os.path.join(BASE_PATH, page2_id, "visuals", name, "visual.json"), json_str)


# Page 3
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
    "slicer_market": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "slicer_market",
  "position": {"x": 10, "y": 110, "z": 0, "height": 80, "width": 200, "tabOrder": 0},
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "market_name"}},
            "queryRef": "mart_volatility_analysis.market_name",
            "nativeQueryRef": "Select Market",
            "active": true
          }]
        }
      }
    },
    "objects": {
      "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
      "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "slicer_candidates": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "slicer_candidates",
  "position": {"x": 10, "y": 200, "z": 1, "height": 250, "width": 200, "tabOrder": 1},
  "visual": {
    "visualType": "slicer",
    "query": {
      "queryState": {
        "Values": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "contract_name"}},
            "queryRef": "mart_anomaly_detection.contract_name",
            "nativeQueryRef": "Select Candidates",
            "active": true
          }]
        }
      }
    },
    "objects": {
      "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'List'"}}}}}],
      "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "card_avg_spread": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_avg_spread",
  "position": {"x": 10, "y": 10, "z": 2, "height": 90, "width": 250, "tabOrder": 2},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "Avg Market Spread"}}, "queryRef": "mart_spread_analysis.Avg Market Spread", "nativeQueryRef": "Avg Spread"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_max_volatility": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_max_volatility",
  "position": {"x": 270, "y": 10, "z": 3, "height": 90, "width": 250, "tabOrder": 3},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "Max Volatility Contract"}}, "queryRef": "mart_volatility_analysis.Max Volatility Contract", "nativeQueryRef": "Most Volatile"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "20D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_reversal": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_reversal",
  "position": {"x": 530, "y": 10, "z": 4, "height": 90, "width": 250, "tabOrder": 4},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "Largest 24H Reversal"}}, "queryRef": "mart_anomaly_detection.Largest 24H Reversal", "nativeQueryRef": "24H Reversal"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "card_anomaly_count": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "card_anomaly_count",
  "position": {"x": 790, "y": 10, "z": 5, "height": 90, "width": 250, "tabOrder": 5},
  "visual": {
    "visualType": "card",
    "query": {"queryState": {"Values": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "Total Anomalies"}}, "queryRef": "mart_anomaly_detection.Total Anomalies", "nativeQueryRef": "Anomaly Count"}]}}},
    "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "28D"}}}}}], "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}]},
    "drillFilterOtherVisuals": true
  }
}""",
    "matrix_volatility": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "matrix_volatility",
  "position": {"x": 220, "y": 110, "z": 6, "height": 290, "width": 660, "tabOrder": 6},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "contract_name"}}, "queryRef": "mart_volatility_analysis.contract_name", "nativeQueryRef": "Contract"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "window_days"}}, "queryRef": "mart_volatility_analysis.window_days", "nativeQueryRef": "Window"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "volatility_score"}}, "queryRef": "mart_volatility_analysis.volatility_score", "nativeQueryRef": "Volatility Score"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "stddev_price"}}, "queryRef": "mart_volatility_analysis.stddev_price", "nativeQueryRef": "Std Dev"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "price_range"}}, "queryRef": "mart_volatility_analysis.price_range", "nativeQueryRef": "Price Range"}
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "scatter_spread": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "scatter_spread",
  "position": {"x": 890, "y": 110, "z": 7, "height": 290, "width": 380, "tabOrder": 7},
  "visual": {
    "visualType": "scatterChart",
    "query": {
      "queryState": {
        "Category": {
          "projections": [{
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "contract_name"}},
            "queryRef": "mart_spread_analysis.contract_name",
            "nativeQueryRef": "Contract",
            "active": true
          }]
        },
        "X": {
          "projections": [{
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_spread_analysis"}}, "Property": "Avg Market Spread"}},
            "queryRef": "mart_spread_analysis.Avg Market Spread",
            "nativeQueryRef": "Avg Spread",
            "active": true
          }]
        },
        "Y": {
          "projections": [{
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "mart_volatility_analysis"}}, "Property": "Avg Volatility"}},
            "queryRef": "mart_volatility_analysis.Avg Volatility",
            "nativeQueryRef": "Implied Volatility"
          }]
        }
      }
    },
    "objects": {
      "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}],
      "fillPoint": [{"properties": {}}]
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "table_anomalies": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "table_anomalies",
  "position": {"x": 220, "y": 410, "z": 8, "height": 300, "width": 460, "tabOrder": 8},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "contract_name"}}, "queryRef": "mart_anomaly_detection.contract_name", "nativeQueryRef": "Contract"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "market_name"}}, "queryRef": "mart_anomaly_detection.market_name", "nativeQueryRef": "Market"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "z_score"}}, "queryRef": "mart_anomaly_detection.z_score", "nativeQueryRef": "Z-Score"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "anomaly_score"}}, "queryRef": "mart_anomaly_detection.anomaly_score", "nativeQueryRef": "Anomaly Score"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "change_24h"}}, "queryRef": "mart_anomaly_detection.change_24h", "nativeQueryRef": "Change 24H"}
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}""",
    "table_signals": """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
  "name": "table_signals",
  "position": {"x": 690, "y": 410, "z": 9, "height": 300, "width": 580, "tabOrder": 9},
  "visual": {
    "visualType": "tableEx",
    "query": {
      "queryState": {
        "Values": {
          "projections": [
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "signal_type"}}, "queryRef": "mart_anomaly_detection.signal_type", "nativeQueryRef": "Signal"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "contract_name"}}, "queryRef": "mart_anomaly_detection.contract_name", "nativeQueryRef": "Contract"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "market_name"}}, "queryRef": "mart_anomaly_detection.market_name", "nativeQueryRef": "Market"},
            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "mart_anomaly_detection"}}, "Property": "signal_strength"}}, "queryRef": "mart_anomaly_detection.signal_strength", "nativeQueryRef": "Strength"}
          ]
        }
      }
    },
    "drillFilterOtherVisuals": true
  }
}"""
}

for name, json_str in visuals_p3.items():
    write_raw_json(os.path.join(BASE_PATH, page3_id, "visuals", name, "visual.json"), json_str)

print("All visuals created successfully!")
