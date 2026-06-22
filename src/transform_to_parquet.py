from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from config import PROCESSED_DIR, RAW_DIR


def latest_raw_file() -> Path:
    files = sorted(RAW_DIR.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No raw JSON files found under {RAW_DIR}")
    return files[0]


def load_json(path: str | Path | None = None) -> dict[str, Any]:
    json_path = Path(path) if path else latest_raw_file()
    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def normalize_predictit(payload: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Flatten PredictIt payload into market and contract tables."""
    extraction_ts = datetime.now(timezone.utc).isoformat()
    markets = payload.get("markets", [])

    market_rows: list[dict[str, Any]] = []
    contract_rows: list[dict[str, Any]] = []

    for market in markets:
        market_id = first_present(market, "id", "ID")
        market_rows.append(
            {
                "market_id": market_id,
                "market_name": first_present(market, "name", "Name"),
                "market_short_name": first_present(market, "shortName", "ShortName"),
                "market_url": first_present(market, "url", "URL"),
                "market_status": first_present(market, "status", "Status"),
                "market_time_stamp": first_present(market, "timeStamp", "TimeStamp"),
                "extraction_ts": extraction_ts,
            }
        )

        for contract in first_present(market, "contracts", "Contracts") or []:
            contract_rows.append(
                {
                    "market_id": market_id,
                    "contract_id": first_present(contract, "id", "ID"),
                    "contract_name": first_present(contract, "name", "Name"),
                    "contract_short_name": first_present(contract, "shortName", "ShortName"),
                    "contract_status": first_present(contract, "status", "Status"),
                    "last_trade_price": first_present(contract, "lastTradePrice", "LastTradePrice"),
                    "best_buy_yes_cost": first_present(contract, "bestBuyYesCost", "BestBuyYesCost"),
                    "best_buy_no_cost": first_present(contract, "bestBuyNoCost", "BestBuyNoCost"),
                    "best_sell_yes_cost": first_present(contract, "bestSellYesCost", "BestSellYesCost"),
                    "best_sell_no_cost": first_present(contract, "bestSellNoCost", "BestSellNoCost"),
                    "last_close_price": first_present(contract, "lastClosePrice", "LastClosePrice"),
                    "display_order": first_present(contract, "displayOrder", "DisplayOrder"),
                    "extraction_ts": extraction_ts,
                }
            )

    return pd.DataFrame(market_rows), pd.DataFrame(contract_rows)


def write_parquet(markets_df: pd.DataFrame, contracts_df: pd.DataFrame, run_ts: datetime | None = None) -> tuple[Path, Path]:
    run_ts = run_ts or datetime.now(timezone.utc)
    output_dir = (
        PROCESSED_DIR
        / f"year={run_ts:%Y}"
        / f"month={run_ts:%m}"
        / f"day={run_ts:%d}"
        / f"hour={run_ts:%H}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    markets_path = output_dir / f"markets_{run_ts:%Y%m%dT%H%M%SZ}.parquet"
    contracts_path = output_dir / f"contracts_{run_ts:%Y%m%dT%H%M%SZ}.parquet"

    markets_df.to_parquet(markets_path, index=False)
    contracts_df.to_parquet(contracts_path, index=False)
    return markets_path, contracts_path


def main(raw_json_path: str | None = None) -> tuple[str, str]:
    payload = load_json(raw_json_path)
    markets_df, contracts_df = normalize_predictit(payload)
    markets_path, contracts_path = write_parquet(markets_df, contracts_df)
    print(f"Saved markets parquet: {markets_path}")
    print(f"Saved contracts parquet: {contracts_path}")
    return str(markets_path), str(contracts_path)


if __name__ == "__main__":
    main()
