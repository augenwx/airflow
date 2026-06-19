from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from config import PREDICTIT_API_URL, RAW_DIR


def fetch_predictit_data(url: str = PREDICTIT_API_URL, timeout: int = 30) -> dict[str, Any]:
    """Download PredictIt market data as JSON."""
    headers = {"User-Agent": "predictit-data-pipeline/1.0"}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def build_raw_path(run_ts: datetime | None = None) -> Path:
    """Create a partitioned raw file path: year=YYYY/month=MM/day=DD/hour=HH."""
    run_ts = run_ts or datetime.now(timezone.utc)
    partition_dir = (
        RAW_DIR
        / f"year={run_ts:%Y}"
        / f"month={run_ts:%m}"
        / f"day={run_ts:%d}"
        / f"hour={run_ts:%H}"
    )
    partition_dir.mkdir(parents=True, exist_ok=True)
    return partition_dir / f"predictit_{run_ts:%Y%m%dT%H%M%SZ}.json"


def save_raw_json(payload: dict[str, Any], output_path: Path | None = None) -> Path:
    output_path = output_path or build_raw_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    return output_path


def main() -> str:
    payload = fetch_predictit_data()
    output_path = save_raw_json(payload)
    print(f"Saved raw PredictIt JSON: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    main()
