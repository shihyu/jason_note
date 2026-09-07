#!/usr/bin/env bash
set -euo pipefail
echo "==> unit tests"
python3 -m pytest tests/unit -v
echo "==> system tests"
python3 -m pytest tests/system -v
echo "==> all tests passed"
