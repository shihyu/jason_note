#!/usr/bin/env bash
set -euo pipefail

echo "==> system tests"
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p no:cacheprovider tests/system
echo "==> all tests passed"
