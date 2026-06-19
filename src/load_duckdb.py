from __future__ import annotations

import duckdb

from config import DUCKDB_PATH, PROCESSED_DIR


def load_parquet_to_duckdb() -> str:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_PATH))

    markets_glob = str(PROCESSED_DIR / "**" / "markets_*.parquet")
    contracts_glob = str(PROCESSED_DIR / "**" / "contracts_*.parquet")

    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(f"""
        CREATE OR REPLACE VIEW raw.markets AS
        SELECT * FROM read_parquet('{markets_glob}', union_by_name=true)
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW raw.contracts AS
        SELECT * FROM read_parquet('{contracts_glob}', union_by_name=true)
    """)

    con.execute("""
        CREATE SCHEMA IF NOT EXISTS analytics;
        CREATE OR REPLACE VIEW analytics.market_contract_prices AS
        SELECT
            c.extraction_ts,
            m.market_id,
            m.market_name,
            c.contract_id,
            c.contract_name,
            TRY_CAST(c.last_trade_price AS DOUBLE) AS last_trade_price,
            TRY_CAST(c.best_buy_yes_cost AS DOUBLE) AS best_buy_yes_cost,
            TRY_CAST(c.best_sell_yes_cost AS DOUBLE) AS best_sell_yes_cost
        FROM raw.contracts c
        LEFT JOIN raw.markets m USING (market_id)
    """)
    con.close()
    print(f"DuckDB database updated: {DUCKDB_PATH}")
    return str(DUCKDB_PATH)


def main() -> None:
    load_parquet_to_duckdb()


if __name__ == "__main__":
    main()
