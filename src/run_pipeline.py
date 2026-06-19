from __future__ import annotations

from extract_predictit import main as extract_main
from load_duckdb import load_parquet_to_duckdb
from transform_to_parquet import main as transform_main


def main() -> None:
    raw_path = extract_main()
    transform_main(raw_path)
    load_parquet_to_duckdb()


if __name__ == "__main__":
    main()
