#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "==> unit tests"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/unit -v
echo "==> system tests"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/system -v
echo "==> all tests passed"
