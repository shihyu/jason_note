#!/bin/bash
# Test script for validating xgotop sampling functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TESTSERVER_BIN="./testserver"
XGOTOP_BIN="./xgotop"
OUTPUT_DIR="./sampling_test_results"
TEST_REQUESTS=5000
CURL_URL="http://localhost/books/test-book/page/100"

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_msg "$YELLOW" "Checking prerequisites..."
    
    # Remove and create output directory
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    print_msg "$GREEN" "Prerequisites OK"
}

# Run a test with specific sampling configuration
run_test() {
    local test_name=$1
    local sample_args=$2
    local output_prefix="${OUTPUT_DIR}/${test_name}"
    
    print_msg "$YELLOW" "\n=== Running test: $test_name ==="

    # Kill any existing processes
    sudo pkill -f "$TESTSERVER_BIN" 2>/dev/null || true
    sudo pkill -f "xgotop" 2>/dev/null || true
    sleep 2
    
    # Start testserver first
    print_msg "$GREEN" "Starting testserver..."
    $TESTSERVER_BIN 2>&1 &
    TESTSERVER_PID=$!
    
    # Give testserver time to start
    sleep 2
    
    # Check if testserver is running
    if ! kill -0 $TESTSERVER_PID 2>/dev/null; then
        print_msg "$RED" "Error: testserver failed to start"
        exit 1
    fi
    
    # Verify testserver is responding
    print_msg "$GREEN" "Verifying testserver is responding..."
    if ! curl -s -f -m 2 "$CURL_URL" > /dev/null 2>&1; then
        print_msg "$RED" "Error: testserver is not responding on $CURL_URL"
        sudo kill -INT $TESTSERVER_PID 2>/dev/null || true
        exit 1
    fi
    print_msg "$GREEN" "Testserver is ready!"
    
    # Start xgotop with sampling configuration
    if [ -z "$sample_args" ]; then
        print_msg "$GREEN" "Starting xgotop (no sampling)..."
        sudo $XGOTOP_BIN -b $TESTSERVER_BIN -s -mfp "${test_name}" &
    else
        print_msg "$GREEN" "Starting xgotop with sampling: $sample_args"
        sudo $XGOTOP_BIN -b $TESTSERVER_BIN -s -mfp "${test_name}" --sample "$sample_args" &
    fi
    
    XGOTOP_PID=$!
    
    # Give xgotop time to initialize
    sleep 2
    
    # Check if xgotop is still running
    if ! kill -0 $XGOTOP_PID 2>/dev/null; then
        print_msg "$RED" "Error: xgotop failed to start"
        sudo kill -INT $TESTSERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # Start curl loop
    print_msg "$GREEN" "Starting curl loop for $TEST_REQUESTS requests..."
    for i in $(seq 1 $TEST_REQUESTS); do
        curl -s "$CURL_URL" > /dev/null 2>&1
    done

    # Wait for all requests to complete
    sleep 3
    print_msg "$GREEN" "All requests completed!"
    
    # Kill testserver (we already have its PID)
    print_msg "$YELLOW" "Stopping testserver..."
    if [ ! -z "$TESTSERVER_PID" ] && kill -0 $TESTSERVER_PID 2>/dev/null; then
        sudo kill -INT $TESTSERVER_PID 2>/dev/null || true
        sleep 1
        # Force kill if still running
        if kill -0 $TESTSERVER_PID 2>/dev/null; then
            sudo kill -9 $TESTSERVER_PID 2>/dev/null || true
        fi
    fi
    
    # Give xgotop time to process remaining events
    sleep 2
    
    # Stop xgotop
    print_msg "$YELLOW" "Stopping xgotop..."
    sudo kill -INT $XGOTOP_PID 2>/dev/null || true
    
    # Wait for xgotop to write metrics
    wait $XGOTOP_PID 2>/dev/null || true
    
    # Find the metrics file
    local metrics_file=$(find . -name "metrics_*${test_name}.json" -type f -mmin -1 | head -1)
    if [ -z "$metrics_file" ]; then
        print_msg "$RED" "Error: Could not find metrics file for $test_name"
        return 1
    fi
    
    # Move metrics file to output directory
    mv "$metrics_file" "${output_prefix}_metrics.json"
    print_msg "$GREEN" "Metrics saved to: ${output_prefix}_metrics.json"
    
    return 0
}

# Main test sequence
main() {
    print_msg "$GREEN" "\n🧪 XGOTOP Sampling Rate Test Suite 🧪\n"
    
    check_prerequisites
    
    # Test 1: Baseline (no sampling)
    run_test "baseline" ""
    
    # Test 2: Uniform 10% sampling
    run_test "uniform_10pct" "newgoroutine:0.1,makemap:0.1,makeslice:0.1,newobject:0.1,goexit:0.1,casgstatus:0.1"
    
    # Test 3: Uniform 50% sampling
    run_test "uniform_50pct" "newgoroutine:0.5,makemap:0.5,makeslice:0.5,newobject:0.5,goexit:0.5,casgstatus:0.5"
    
    # Test 4: Mixed sampling rates
    run_test "mixed" "newgoroutine:0.8,makemap:0.2,makeslice:0.1,newobject:0.5,goexit:0.7,casgstatus:0.05"
    
    # Test 5: Selective sampling (only makemap)
    run_test "selective_makemap" "makemap:0.01"
    
    # Test 6: High-frequency sampling
    run_test "high_freq" "newgoroutine:0.99,makemap:0.95,makeslice:0.9,newobject:0.85,goexit:0.95,casgstatus:0.95"
    
    print_msg "$GREEN" "\n✅ All tests completed!"
    print_msg "$YELLOW" "\nValidating results..."
    
    # Run validation if the script exists
    if [ -f "./scripts/validate_sampling.py" ]; then
        print_msg "$YELLOW" "Validating baseline vs uniform_10pct..."
        python3 ./scripts/validate_sampling.py \
            "${OUTPUT_DIR}/baseline_metrics.json" \
            "${OUTPUT_DIR}/uniform_10pct_metrics.json" \
            "newgoroutine:0.1,makemap:0.1,makeslice:0.1,newobject:0.1,goexit:0.1,casgstatus:0.1"

        print_msg "$YELLOW" "Validating baseline vs uniform_50pct..."
        python3 ./scripts/validate_sampling.py \
            "${OUTPUT_DIR}/baseline_metrics.json" \
            "${OUTPUT_DIR}/uniform_50pct_metrics.json" \
            "newgoroutine:0.5,makemap:0.5,makeslice:0.5,newobject:0.5,goexit:0.5,casgstatus:0.5"
            
        print_msg "$YELLOW" "Validating baseline vs mixed..."
        python3 ./scripts/validate_sampling.py \
            "${OUTPUT_DIR}/baseline_metrics.json" \
            "${OUTPUT_DIR}/mixed_metrics.json" \
            "newgoroutine:0.8,makemap:0.2,makeslice:0.1,newobject:0.5,goexit:0.7,casgstatus:0.05"

        print_msg "$YELLOW" "Validating baseline vs selective_makemap..."
        python3 ./scripts/validate_sampling.py \
            "${OUTPUT_DIR}/baseline_metrics.json" \
            "${OUTPUT_DIR}/selective_makemap_metrics.json" \
            "makemap:0.01"

        print_msg "$YELLOW" "Validating baseline vs high_freq..."
        python3 ./scripts/validate_sampling.py \
            "${OUTPUT_DIR}/baseline_metrics.json" \
            "${OUTPUT_DIR}/high_freq_metrics.json" \
            "newgoroutine:0.99,makemap:0.95,makeslice:0.9,newobject:0.85,goexit:0.95,casgstatus:0.95"
    fi
    
    print_msg "$GREEN" "\nTest results saved in: $OUTPUT_DIR"
    print_msg "$YELLOW" "\nTo manually validate results, run:"
    print_msg "$NC" "  python3 scripts/validate_sampling.py ${OUTPUT_DIR}/baseline_metrics.json ${OUTPUT_DIR}/<test>_metrics.json '<sampling_rates>'"
}

# Run main function
main
