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

DATA_WAREHOUSE = os.getenv("DATA_WAREHOUSE", "snowflake").lower()

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "PREDICTIT")
SNOWFLAKE_RAW_SCHEMA = os.getenv("SNOWFLAKE_RAW_SCHEMA", "RAW")
SNOWFLAKE_STAGE = os.getenv("SNOWFLAKE_STAGE", "PREDICTIT_PARQUET_STAGE")
