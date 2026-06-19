from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parents[1])).resolve()
PREDICTIT_API_URL = os.getenv("PREDICTIT_API_URL", "https://www.predictit.org/api/marketdata/all/")
DUCKDB_PATH = PROJECT_ROOT / os.getenv("DUCKDB_PATH", "data/warehouse/predictit.duckdb")
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "predictit"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "predictit"
