#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variable to track if we should run cleanup
SHOULD_CLEANUP=false

# Cleanup function to kill all processes on interrupt
cleanup() {
    if [ "$SHOULD_CLEANUP" = true ]; then
        echo -e "${YELLOW}Interrupted! Cleaning up processes...${NC}"

        # Kill any remaining curl processes
        pkill -f "curl.*$CURL_URL" 2>/dev/null || true

        # Kill xgotop if running
        sudo pkill -f "xgotop" 2>/dev/null || true

        # Kill testserver if running
        sudo pkill -f "$TESTSERVER_BIN" 2>/dev/null || true

        echo -e "${GREEN}Cleanup complete${NC}"
    fi
}

# Set trap to cleanup on interrupt only
trap 'SHOULD_CLEANUP=true; cleanup' INT TERM

# Configuration
TESTSERVER_BIN="./testserver"
XGOTOP_BIN="./xgotop"
OUTPUT_DIR="./web_overhead_test_results"
TEST_REQUESTS=10000
CURL_URL="http://localhost/books/test-book/page/100"
PLOT_SCRIPT="./plot_metrics.py"

# Default ranges (can be overridden by command line arguments)
READERS_RANGE="1 2 3 4 5"
PROCESSORS_RANGE="1 2 3 4 5"
WEB_MODES="0 1"  # By default test both modes
FLOOD_MODE=false  # Default to normal mode (wait for responses)
STORAGE_FORMATS="jsonl"  # Default storage formats to test (can be "jsonl protobuf" for all)
BATCH_SIZES=""  # Default empty (uses xgotop default of 1000), can be "100 500 1000 2000" for testing

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

run_test() {
    local readers_count=$1
    local processors_count=$2
    local web_mode=$3
    local storage_format=$4
    local batch_size=$5

    # Build metrics file prefix
    local metrics_file_prefix="readers_${readers_count}_processors_${processors_count}_web_${web_mode}_${storage_format}"
    if [ ! -z "$batch_size" ]; then
        metrics_file_prefix="${metrics_file_prefix}_batch_${batch_size}"
    fi
    local output_prefix="${OUTPUT_DIR}/${metrics_file_prefix}"

    # Build test description
    local test_desc="$readers_count readers, $processors_count processors, web mode $web_mode, storage $storage_format"
    if [ ! -z "$batch_size" ]; then
        test_desc="$test_desc, batch size $batch_size"
    fi
    print_msg "$YELLOW" "\n=== Running test: $test_desc ==="

    # Enable cleanup on interrupt from this point
    SHOULD_CLEANUP=true

    # Kill any existing processes
    sudo pkill -f "$TESTSERVER_BIN" 2>/dev/null || true
    sudo pkill -f "xgotop" 2>/dev/null || true
    sleep 1
    
    # Start testserver first
    print_msg "$GREEN" "Starting testserver..."
    $TESTSERVER_BIN 2>&1 &
    TESTSERVER_PID=$!
    
    # Give testserver time to start
    sleep 1
    
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
        
    # Build batch size parameter
    local batch_param=""
    if [ ! -z "$batch_size" ]; then
        batch_param="-batch-size $batch_size"
    fi

    if [ $web_mode -eq 1 ]; then
        local desc_msg="Starting xgotop with web mode, $readers_count readers, $processors_count processors, storage: $storage_format"
        if [ ! -z "$batch_size" ]; then
            desc_msg="$desc_msg, batch size: $batch_size"
        fi
        print_msg "$GREEN" "$desc_msg"
        sudo $XGOTOP_BIN -b $TESTSERVER_BIN -s -web -storage-format "$storage_format" -rw $readers_count -pw $processors_count -mfp "${metrics_file_prefix}" $batch_param &
    else
        local desc_msg="Starting xgotop with no web mode, $readers_count readers, $processors_count processors, storage: $storage_format"
        if [ ! -z "$batch_size" ]; then
            desc_msg="$desc_msg, batch size: $batch_size"
        fi
        print_msg "$GREEN" "$desc_msg"
        sudo $XGOTOP_BIN -b $TESTSERVER_BIN -s -storage-format "$storage_format" -rw $readers_count -pw $processors_count -mfp "${metrics_file_prefix}" $batch_param &
    fi
    
    XGOTOP_PID=$!
    
    # Give xgotop time to initialize
    sleep 1
    
    # Check if xgotop is still running
    if ! kill -0 $XGOTOP_PID 2>/dev/null; then
        print_msg "$RED" "Error: xgotop failed to start"
        sudo kill -INT $TESTSERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # Start curl loop
    if [ "$FLOOD_MODE" = true ]; then
        print_msg "$GREEN" "Starting curl FLOOD mode for $TEST_REQUESTS requests..."

        # Store PIDs of background curl processes
        CURL_PIDS=()
        for i in $(seq 1 $TEST_REQUESTS); do
            curl -s "$CURL_URL" > /dev/null 2>&1 &
            CURL_PIDS+=($!)
        done

        # Wait for all background curl processes to complete with timeout
        print_msg "$YELLOW" "Waiting for all background requests to complete..."

        # Give processes time to complete naturally
        WAIT_TIME=0
        MAX_WAIT=30  # Maximum 30 seconds wait
        while [ $WAIT_TIME -lt $MAX_WAIT ]; do
            # Check if any curl processes are still running
            STILL_RUNNING=0
            for pid in "${CURL_PIDS[@]}"; do
                if kill -0 $pid 2>/dev/null; then
                    STILL_RUNNING=$((STILL_RUNNING + 1))
                fi
            done

            if [ $STILL_RUNNING -eq 0 ]; then
                print_msg "$GREEN" "All flood requests completed!"
                break
            fi

            if [ $((WAIT_TIME % 5)) -eq 0 ]; then
                print_msg "$YELLOW" "  Still waiting for $STILL_RUNNING requests to complete..."
            fi

            sleep 1
            WAIT_TIME=$((WAIT_TIME + 1))
        done

        # Force kill any remaining curl processes after timeout
        if [ $WAIT_TIME -ge $MAX_WAIT ]; then
            print_msg "$RED" "Timeout reached, killing remaining curl processes..."
            for pid in "${CURL_PIDS[@]}"; do
                kill -9 $pid 2>/dev/null || true
            done
        fi

        sleep 1
    else
        print_msg "$GREEN" "Starting curl loop for $TEST_REQUESTS requests..."
        for i in $(seq 1 $TEST_REQUESTS); do
            curl -s "$CURL_URL" > /dev/null 2>&1
        done

        # Wait for all requests to complete
        sleep 3
        print_msg "$GREEN" "All requests completed!"
    fi

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
    
    # Stop xgotop
    print_msg "$YELLOW" "Stopping xgotop..."
    sudo kill -INT $XGOTOP_PID 2>/dev/null || true
    
    # Wait for xgotop to write metrics
    wait $XGOTOP_PID 2>/dev/null || true
    
    # Find the metrics file (extract basename from output_prefix for the pattern)
    local metrics_file=$(find . -name "metrics_*${metrics_file_prefix}.json" -type f -mmin -1 | head -1)
    if [ -z "$metrics_file" ]; then
        print_msg "$RED" "Error: Could not find metrics file for $output_prefix"
        return 1
    fi
    
    # Move metrics file to output directory
    mv "$metrics_file" "${output_prefix}_metrics.json"
    print_msg "$GREEN" "Metrics saved to: ${output_prefix}_metrics.json"

    # Disable cleanup since test completed successfully
    SHOULD_CLEANUP=false

    return 0
}

# Function to generate plot after tests complete
generate_plots() {
    print_msg "$BLUE" "\n📊 Generating plots from test results..."

    # Check if plot script exists
    if [ ! -f "$PLOT_SCRIPT" ]; then
        print_msg "$RED" "Error: Plot script not found at $PLOT_SCRIPT"
        return 1
    fi

    # Check if virtual environment exists
    if [ -d "env" ]; then
        source env/bin/activate
    fi

    # Build the --files argument for plot_metrics.py
    local files_args=""
    for r in $READERS_RANGE; do
        for p in $PROCESSORS_RANGE; do
            for w in $WEB_MODES; do
                for s in $STORAGE_FORMATS; do
                    # If batch sizes are specified, include them in the search
                    if [ ! -z "$BATCH_SIZES" ]; then
                        for b in $BATCH_SIZES; do
                            local label="r${r}_p${p}_w${w}_${s}_b${b}"
                            local file_path="${OUTPUT_DIR}/readers_${r}_processors_${p}_web_${w}_${s}_batch_${b}_metrics.json"
                            if [ -f "$file_path" ]; then
                                files_args="${files_args} '${label}:${file_path}'"
                            fi
                        done
                    else
                        # Default case without batch size in filename
                        local label="r${r}_p${p}_w${w}_${s}"
                        local file_path="${OUTPUT_DIR}/readers_${r}_processors_${p}_web_${w}_${s}_metrics.json"
                        if [ -f "$file_path" ]; then
                            files_args="${files_args} '${label}:${file_path}'"
                        fi
                    fi
                done
            done
        done
    done

    if [ -z "$files_args" ]; then
        print_msg "$RED" "Error: No metrics files found to plot"
        return 1
    fi

    # Generate timestamp for output filename
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local output_file="web_overhead_test_${timestamp}.png"

    print_msg "$GREEN" "Run the following command to generate metric plots: python3 $PLOT_SCRIPT --files $files_args --mode new -o $output_file"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -r|--readers)
                READERS_RANGE="$2"
                shift 2
                ;;
            -p|--processors)
                PROCESSORS_RANGE="$2"
                shift 2
                ;;
            -n|--requests)
                TEST_REQUESTS="$2"
                shift 2
                ;;
            --only-web)
                WEB_MODES="1"
                shift
                ;;
            --no-web)
                WEB_MODES="0"
                shift
                ;;
            --flood)
                FLOOD_MODE=true
                shift
                ;;
            --storage)
                STORAGE_FORMATS="$2"
                shift 2
                ;;
            --batch-sizes)
                BATCH_SIZES="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  -r, --readers RANGE      Set reader counts (default: '1 2 3 4 5')"
                echo "  -p, --processors RANGE   Set processor counts (default: '1 2 3 4 5')"
                echo "  -n, --requests NUM       Number of test requests (default: 10000)"
                echo "  --only-web               Test only with web mode enabled"
                echo "  --no-web                 Test only with web mode disabled"
                echo "  --flood                  Flood mode - run curl requests in background without waiting"
                echo "  --storage FORMATS        Storage formats to test: 'jsonl', 'protobuf', or combinations (default: jsonl)"
                echo "  --batch-sizes SIZES      Batch sizes to test: e.g. '100 500 1000 2000' (default: uses xgotop default)"
                echo "  -h, --help               Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                                    # Run with defaults (both web modes)"
                echo "  $0 -r '1 2 3' -p '1 2 3'             # Test with 1-3 readers and processors"
                echo "  $0 -r '2 4 6 8' -p '1 2 3 4'         # Custom ranges"
                echo "  $0 --only-web                        # Test only with web mode enabled"
                echo "  $0 --no-web                          # Test only with web mode disabled"
                echo "  $0 --flood -n 50000                  # Flood mode with 50000 concurrent requests"
                echo "  $0 --storage 'jsonl protobuf'        # Test all storage formats"
                echo "  $0 --batch-sizes '100 500 1000 2000' # Test different batch sizes"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Main test sequence
main() {
    # Parse command line arguments
    parse_args "$@"

    print_msg "$GREEN" "\n🧪 XGOTOP Web Overhead Test Suite 🧪\n"
    print_msg "$BLUE" "Configuration:"
    print_msg "$BLUE" "  Readers: $READERS_RANGE"
    print_msg "$BLUE" "  Processors: $PROCESSORS_RANGE"
    print_msg "$BLUE" "  Requests per test: $TEST_REQUESTS"
    print_msg "$BLUE" "  Output directory: $OUTPUT_DIR"
    print_msg "$BLUE" "  Storage formats: $STORAGE_FORMATS"

    # Show batch sizes configuration
    if [ ! -z "$BATCH_SIZES" ]; then
        print_msg "$BLUE" "  Batch sizes: $BATCH_SIZES"
    else
        print_msg "$BLUE" "  Batch sizes: DEFAULT (xgotop default of 1000)"
    fi

    # Show web mode configuration
    if [ "$WEB_MODES" = "1" ]; then
        print_msg "$BLUE" "  Web mode: ONLY WEB (--only-web)"
    elif [ "$WEB_MODES" = "0" ]; then
        print_msg "$BLUE" "  Web mode: NO WEB (--no-web)"
    else
        print_msg "$BLUE" "  Web mode: BOTH (testing with and without web)"
    fi

    # Show flood mode status
    if [ "$FLOOD_MODE" = true ]; then
        print_msg "$YELLOW" "  Request mode: FLOOD MODE (concurrent requests without waiting)"
    else
        print_msg "$BLUE" "  Request mode: NORMAL (sequential requests with response wait)"
    fi

    check_prerequisites

    # Calculate total tests
    local reader_count=$(echo $READERS_RANGE | wc -w)
    local processor_count=$(echo $PROCESSORS_RANGE | wc -w)
    local web_mode_count=$(echo $WEB_MODES | wc -w)
    local storage_count=$(echo $STORAGE_FORMATS | wc -w)
    # If batch sizes are specified, use that count; otherwise default test count = 1
    local batch_count=1
    if [ ! -z "$BATCH_SIZES" ]; then
        batch_count=$(echo $BATCH_SIZES | wc -w)
    fi
    total_tests=$((reader_count * processor_count * web_mode_count * storage_count * batch_count))
    current_test=0

    # If batch sizes are not specified, use empty string to run with default
    local batch_sizes_to_test="$BATCH_SIZES"
    if [ -z "$BATCH_SIZES" ]; then
        batch_sizes_to_test=""  # This will run once with no batch size parameter
    fi

    for readers in $READERS_RANGE; do
        for processors in $PROCESSORS_RANGE; do
            for web_mode in $WEB_MODES; do
                for storage in $STORAGE_FORMATS; do
                    # If batch sizes are specified, loop through them
                    if [ ! -z "$BATCH_SIZES" ]; then
                        for batch in $BATCH_SIZES; do
                            current_test=$((current_test + 1))
                            print_msg "$YELLOW" "\n>>> Progress: $current_test/$total_tests tests"
                            run_test $readers $processors $web_mode $storage $batch
                        done
                    else
                        # Run once with no batch size specified (uses default)
                        current_test=$((current_test + 1))
                        print_msg "$YELLOW" "\n>>> Progress: $current_test/$total_tests tests"
                        run_test $readers $processors $web_mode $storage ""
                    fi
                done
            done
        done
    done

    print_msg "$GREEN" "\n✅ All tests completed!"
    generate_plots
}

# Run main function with all arguments
main "$@"
