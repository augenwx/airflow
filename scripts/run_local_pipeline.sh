#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PROJECT_ROOT
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

python "$PROJECT_ROOT/src/run_pipeline.py"
