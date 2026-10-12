#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "==> unit tests: not applicable to documentation-only changes (see plan.md)"
echo "==> system tests"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/system -v
echo "==> all tests passed"
