#!/bin/bash
#
# Performance Comparison Script
# Compares original vs HFT-optimized clients
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test parameters
NUM_ORDERS=${1:-1000}
NUM_CONNECTIONS=${2:-100}
NUM_WARMUP=${3:-100}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BASE_DIR="$(dirname "$PROJECT_ROOT")"

echo "=========================================="
echo "  HFT Performance Comparison"
echo "=========================================="
echo "Test parameters:"
echo "  Orders: $NUM_ORDERS"
echo "  Connections: $NUM_CONNECTIONS"
echo "  Warmup: $NUM_WARMUP"
echo ""

# Check if server is running
check_server() {
    if ! curl -s http://localhost:8080/stats > /dev/null 2>&1; then
        echo -e "${RED}Error: Server not running on localhost:8080${NC}"
        echo "Please start the server first:"
        echo "  cd $BASE_DIR/rust-api-server && cargo run --release"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Server is running"
}

# Build clients
build_clients() {
    echo ""
    echo "Building clients..."

    # Build original C client
    echo -n "  Building original C client... "
    cd "$BASE_DIR/c-client"
    make clean > /dev/null 2>&1
    make > /dev/null 2>&1
    echo -e "${GREEN}✓${NC}"

    # Build HFT-optimized C client
    echo -n "  Building HFT-optimized C client... "
    cd "$PROJECT_ROOT/c-client"
    make clean > /dev/null 2>&1
    make > /dev/null 2>&1
    echo -e "${GREEN}✓${NC}"

    echo ""
}

# Run test
run_test() {
    local name=$1
    local client_path=$2
    local args=$3

    echo "=========================================="
    echo "Running: $name"
    echo "=========================================="

    # Reset server stats
    curl -s http://localhost:8080/stats > /dev/null 2>&1

    # Run client
    cd "$(dirname "$client_path")"
    eval "./$(basename "$client_path") $args"

    echo ""
}

# Main
main() {
    check_server
    build_clients

    # Test 1: Original C Client
    run_test "Original C Client" \
        "$BASE_DIR/c-client/c_client" \
        "$NUM_ORDERS $NUM_CONNECTIONS $NUM_WARMUP"

    # Save results
    ORIGINAL_RESULT=$(mktemp)
    cd "$BASE_DIR/c-client"
    ./c_client $NUM_ORDERS $NUM_CONNECTIONS $NUM_WARMUP > "$ORIGINAL_RESULT" 2>&1

    sleep 2

    # Test 2: HFT-Optimized C Client
    run_test "HFT-Optimized C Client" \
        "$PROJECT_ROOT/c-client/c_client_hft" \
        "$NUM_ORDERS $NUM_CONNECTIONS $NUM_WARMUP"

    # Save results
    HFT_RESULT=$(mktemp)
    cd "$PROJECT_ROOT/c-client"
    ./c_client_hft $NUM_ORDERS $NUM_CONNECTIONS $NUM_WARMUP > "$HFT_RESULT" 2>&1

    # Compare results
    echo ""
    echo "=========================================="
    echo "  Performance Summary"
    echo "=========================================="
    echo ""

    # Extract metrics
    extract_metric() {
        local file=$1
        local metric=$2
        grep "$metric" "$file" | awk '{print $(NF-1)}' | tail -1
    }

    ORIG_P50=$(extract_metric "$ORIGINAL_RESULT" "P50:")
    ORIG_P99=$(extract_metric "$ORIGINAL_RESULT" "P99:")
    ORIG_AVG=$(extract_metric "$ORIGINAL_RESULT" "Avg latency:")
    ORIG_THROUGHPUT=$(extract_metric "$ORIGINAL_RESULT" "Throughput:")

    HFT_P50=$(extract_metric "$HFT_RESULT" "P50:")
    HFT_P99=$(extract_metric "$HFT_RESULT" "P99:")
    HFT_AVG=$(extract_metric "$HFT_RESULT" "Avg latency:")
    HFT_THROUGHPUT=$(extract_metric "$HFT_RESULT" "Throughput:")

    # Calculate improvements
    calc_improvement() {
        local orig=$1
        local hft=$2
        echo "scale=2; (($orig - $hft) / $orig) * 100" | bc
    }

    P50_IMP=$(calc_improvement "$ORIG_P50" "$HFT_P50" || echo "N/A")
    P99_IMP=$(calc_improvement "$ORIG_P99" "$HFT_P99" || echo "N/A")
    AVG_IMP=$(calc_improvement "$ORIG_AVG" "$HFT_AVG" || echo "N/A")
    THROUGHPUT_IMP=$(echo "scale=2; (($HFT_THROUGHPUT - $ORIG_THROUGHPUT) / $ORIG_THROUGHPUT) * 100" | bc || echo "N/A")

    printf "%-20s %15s %15s %15s\n" "Metric" "Original" "HFT-Optimized" "Improvement"
    echo "------------------------------------------------------------------------"
    printf "%-20s %12s ms %12s ms %12s%%\n" "P50 Latency" "$ORIG_P50" "$HFT_P50" "$P50_IMP"
    printf "%-20s %12s ms %12s ms %12s%%\n" "P99 Latency" "$ORIG_P99" "$HFT_P99" "$P99_IMP"
    printf "%-20s %12s ms %12s ms %12s%%\n" "Avg Latency" "$ORIG_AVG" "$HFT_AVG" "$AVG_IMP"
    printf "%-20s %12s/s %12s/s %12s%%\n" "Throughput" "$ORIG_THROUGHPUT" "$HFT_THROUGHPUT" "$THROUGHPUT_IMP"

    echo ""
    echo "=========================================="

    # Cleanup
    rm -f "$ORIGINAL_RESULT" "$HFT_RESULT"
}

main