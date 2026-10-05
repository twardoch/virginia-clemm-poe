#!/usr/bin/env bash
# this_file: test.sh
set -euo pipefail
# Execute all regression tests; measure the new discovery module separately.
uv run pytest --no-cov "$@"
uv run pytest tests/test_vendors.py --override-ini addopts= --cov=virginia_clemm_poe.vendors --cov-report=term-missing --cov-fail-under=85
