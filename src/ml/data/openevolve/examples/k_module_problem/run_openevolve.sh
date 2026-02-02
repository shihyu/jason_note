#!/bin/bash
# Run OpenEvolve on the K-Module Problem
#
# Usage: ./run_openevolve.sh [iterations]
#
# Make sure OPENROUTER_API_KEY is set in your environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ITERATIONS=${1:-50}

echo "=============================================="
echo "Running OpenEvolve on K-Module Problem"
echo "=============================================="
echo "Iterations: $ITERATIONS"
echo "Config: config.yaml"
echo ""

# Check for API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Warning: OPENROUTER_API_KEY not set"
    echo "Set it with: export OPENROUTER_API_KEY=your_key"
fi

# Run OpenEvolve
cd "$SCRIPT_DIR"
openevolve-run initial_program.py evaluator.py \
    --config config.yaml \
    --iterations "$ITERATIONS"

echo ""
echo "=============================================="
echo "OpenEvolve run complete!"
echo "Results saved to: openevolve_output/"
echo "=============================================="
