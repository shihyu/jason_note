#!/bin/bash
# Run Iterative Agent on the K-Module Problem
#
# Usage: ./run_iterative.sh [iterations]
#
# Prerequisites:
#   1. Clone the agentic-code-optimization repo:
#      git clone https://github.com/ratulm/agentic-code-optimization.git
#
#   2. Set environment variables:
#      export MODEL_PROVIDER=gemini
#      export GOOGLE_API_KEY=your_key
#
#   OR for OpenRouter:
#      export MODEL_PROVIDER=openai
#      export OPENAI_API_KEY=your_openrouter_key
#      export OPENAI_API_BASE=https://openrouter.ai/api/v1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ITERATIONS=${1:-50}
AGENT_REPO="${AGENT_REPO:-$HOME/agentic-code-optimization}"

echo "=============================================="
echo "Running Iterative Agent on K-Module Problem"
echo "=============================================="
echo "Iterations: $ITERATIONS"
echo "Agent repo: $AGENT_REPO"
echo ""

# Check if agent repo exists
if [ ! -d "$AGENT_REPO" ]; then
    echo "Error: agentic-code-optimization repo not found at $AGENT_REPO"
    echo ""
    echo "Please clone it first:"
    echo "  git clone https://github.com/ratulm/agentic-code-optimization.git $AGENT_REPO"
    echo ""
    echo "Or set AGENT_REPO environment variable to the correct path"
    exit 1
fi

# Check for API key
if [ -z "$GOOGLE_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: No API key found"
    echo "Set GOOGLE_API_KEY for Gemini or OPENAI_API_KEY for OpenRouter"
fi

# Create output directory
OUTPUT_DIR="$SCRIPT_DIR/iterative_output"
mkdir -p "$OUTPUT_DIR"

# Copy files to agent repo examples (required by the agent)
EXAMPLE_DIR="$AGENT_REPO/examples/k_module"
mkdir -p "$EXAMPLE_DIR"
cp "$SCRIPT_DIR/initial_program.py" "$EXAMPLE_DIR/"
cp "$SCRIPT_DIR/evaluator.py" "$EXAMPLE_DIR/"

echo "Running iterative agent..."
cd "$AGENT_REPO"

# Set model provider if not set
export MODEL_PROVIDER="${MODEL_PROVIDER:-gemini}"

# Run the agent
python code_optimization.py \
    --initial-program "$EXAMPLE_DIR/initial_program.py" \
    --evaluator "$EXAMPLE_DIR/evaluator.py" \
    --iterations "$ITERATIONS"

# Copy results back
if [ -d "$AGENT_REPO/outputs" ]; then
    cp -r "$AGENT_REPO/outputs"/* "$OUTPUT_DIR/" 2>/dev/null || true
fi

echo ""
echo "=============================================="
echo "Iterative agent run complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "=============================================="
