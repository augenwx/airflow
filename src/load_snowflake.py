from __future__ import annotations

from pathlib import Path
from typing import Iterable

import snowflake.connector

from config import (
    PROCESSED_DIR,
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_PASSWORD,
    SNOWFLAKE_RAW_SCHEMA,
    SNOWFLAKE_ROLE,
    SNOWFLAKE_STAGE,
    SNOWFLAKE_USER,
    SNOWFLAKE_WAREHOUSE,
)


REQUIRED_ENV_VARS = {
    "SNOWFLAKE_ACCOUNT": SNOWFLAKE_ACCOUNT,
    "SNOWFLAKE_USER": SNOWFLAKE_USER,
    "SNOWFLAKE_PASSWORD": SNOWFLAKE_PASSWORD,
    "SNOWFLAKE_WAREHOUSE": SNOWFLAKE_WAREHOUSE,
}


def _require_snowflake_config() -> None:
    missing = [name for name, value in REQUIRED_ENV_VARS.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing Snowflake configuration. Set these environment variables: "
            + ", ".join(missing)
        )


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _qualified_table(table_name: str) -> str:
    return ".".join(
        [
            _quote_identifier(SNOWFLAKE_DATABASE),
            _quote_identifier(SNOWFLAKE_RAW_SCHEMA),
            _quote_identifier(table_name),
        ]
    )


def _stage_name() -> str:
    return ".".join(
        [
            _quote_identifier(SNOWFLAKE_DATABASE),
            _quote_identifier(SNOWFLAKE_RAW_SCHEMA),
            _quote_identifier(SNOWFLAKE_STAGE),
        ]
    )


def _connect():
    _require_snowflake_config()
    kwargs = {
        "account": SNOWFLAKE_ACCOUNT,
        "user": SNOWFLAKE_USER,
        "password": SNOWFLAKE_PASSWORD,
        "warehouse": SNOWFLAKE_WAREHOUSE,
    }
    if SNOWFLAKE_ROLE:
        kwargs["role"] = SNOWFLAKE_ROLE
    return snowflake.connector.connect(**kwargs)


def _latest_parquet_pair() -> tuple[Path, Path]:
    markets = sorted(
        PROCESSED_DIR.rglob("markets_*.parquet"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    contracts = sorted(
        PROCESSED_DIR.rglob("contracts_*.parquet"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not markets or not contracts:
        raise FileNotFoundError(f"No processed Parquet files found under {PROCESSED_DIR}")
    return markets[0], contracts[0]


def _local_file_uri(path: Path) -> str:
    return "file://" + path.resolve().as_posix()


def _create_raw_objects(cursor) -> None:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {_quote_identifier(SNOWFLAKE_DATABASE)}")
    cursor.execute(f"USE DATABASE {_quote_identifier(SNOWFLAKE_DATABASE)}")
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {_quote_identifier(SNOWFLAKE_DATABASE)}.{_quote_identifier(SNOWFLAKE_RAW_SCHEMA)}")
    cursor.execute(f"USE SCHEMA {_quote_identifier(SNOWFLAKE_RAW_SCHEMA)}")
    cursor.execute(f"CREATE STAGE IF NOT EXISTS {_stage_name()}")
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {_qualified_table("MARKETS")} (
            market_id VARCHAR,
            market_name VARCHAR,
            market_short_name VARCHAR,
            market_url VARCHAR,
            market_status VARCHAR,
            market_time_stamp TIMESTAMP_NTZ,
            extraction_ts TIMESTAMP_NTZ
        )
        """
    )
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {_qualified_table("CONTRACTS")} (
            market_id VARCHAR,
            contract_id VARCHAR,
            contract_name VARCHAR,
            contract_short_name VARCHAR,
            contract_status VARCHAR,
            last_trade_price FLOAT,
            best_buy_yes_cost FLOAT,
            best_buy_no_cost FLOAT,
            best_sell_yes_cost FLOAT,
            best_sell_no_cost FLOAT,
            last_close_price FLOAT,
            display_order INTEGER,
            extraction_ts TIMESTAMP_NTZ
        )
        """
    )


def _put_file(cursor, path: Path, stage_prefix: str) -> None:
    cursor.execute(
        f"PUT '{_local_file_uri(path)}' @{_stage_name()}/{stage_prefix} "
        "AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
    )


def _copy_into(cursor, table_name: str, stage_prefix: str) -> None:
    cursor.execute(
        f"""
        COPY INTO {_qualified_table(table_name)}
        FROM @{_stage_name()}/{stage_prefix}
        FILE_FORMAT = (TYPE = PARQUET USE_LOGICAL_TYPE = TRUE)
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        ON_ERROR = ABORT_STATEMENT
        """
    )


def load_parquet_to_snowflake(parquet_paths: Iterable[str | Path] | None = None) -> str:
    if parquet_paths:
        paths = [Path(path) for path in parquet_paths]
    else:
        paths = list(_latest_parquet_pair())

    markets_paths = [path for path in paths if path.name.startswith("markets_")]
    contracts_paths = [path for path in paths if path.name.startswith("contracts_")]
    if not markets_paths or not contracts_paths:
        raise ValueError("Expected at least one markets_*.parquet and one contracts_*.parquet file.")

    with _connect() as conn:
        cursor = conn.cursor()
        try:
            _create_raw_objects(cursor)
            for path in markets_paths:
                _put_file(cursor, path, "markets")
            for path in contracts_paths:
                _put_file(cursor, path, "contracts")
            _copy_into(cursor, "MARKETS", "markets")
            _copy_into(cursor, "CONTRACTS", "contracts")
        finally:
            cursor.close()

    destination = f"{SNOWFLAKE_DATABASE}.{SNOWFLAKE_RAW_SCHEMA}"
    print(f"Snowflake raw tables updated: {destination}.MARKETS, {destination}.CONTRACTS")
    return destination


def main(parquet_paths: Iterable[str | Path] | None = None) -> str:
    return load_parquet_to_snowflake(parquet_paths)


if __name__ == "__main__":
    main()
