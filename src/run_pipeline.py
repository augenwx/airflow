from __future__ import annotations

import sys
from pathlib import Path

# Add the src and project root directory to sys.path to prevent import errors
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

PROJECT_ROOT = SRC_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extract_predictit import main as extract_main
from src.transform_to_parquet import main as transform_main
from src.load_duckdb import main as load_main


def main() -> None:
    extract_main()
    transform_main()
    load_main()


if __name__ == "__main__":
    main()
