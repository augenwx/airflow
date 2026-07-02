from app import DB_PATH, SCHEMA, query


TABLES = [
    "mart_market_snapshot",
    "mart_top_movers",
    "mart_anomaly_detection",
    "mart_spread_analysis",
    "mart_volatility_analysis",
]


print(f"DuckDB: {DB_PATH}")
print(f"Schema: {SCHEMA}")

for table in TABLES:
    try:
        stats = query(
            f"""
            SELECT
                COUNT(*) AS rows,
                COUNT(DISTINCT market_name) AS markets,
                COUNT(DISTINCT contract_name) AS contracts,
                MAX(extraction_ts) AS latest_ts
            FROM {SCHEMA}.{table}
            """
        )
        row = stats.iloc[0].to_dict()
        print(
            f"{table}: rows={row['rows']}, markets={row['markets']}, "
            f"contracts={row['contracts']}, latest_ts={row['latest_ts']}"
        )
    except Exception as exc:
        print(f"{table}: ERROR: {exc}")
