#!/bin/bash

echo "==================================="
echo "API Performance Benchmark Test"
echo "==================================="
echo

# Configuration
NUM_ORDERS=5000
NUM_CONNECTIONS=200
WARMUP=500

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if server is running
check_server() {
    echo -n "Checking if API server is running on port 8080... "
    if curl -s http://localhost:8080/stats > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}NOT RUNNING${NC}"
        echo
        echo "Please start the API server first:"
        echo "  cd rust-api-server && cargo run --release"
        echo
        return 1
    fi
}

# Build all clients
build_clients() {
    echo -e "${YELLOW}Building all clients...${NC}"
    echo
    
    # Build Rust server (if not running)
    echo -e "${BLUE}Building Rust API Server...${NC}"
    (cd rust-api-server && cargo build --release)
    
    # Build Rust client
    echo -e "${BLUE}Building Rust Client...${NC}"
    (cd rust-client && cargo build --release)
    
    # Build C++ client
    echo -e "${BLUE}Building C++ Client...${NC}"
    if [ ! -d "build" ]; then
        mkdir build
    fi
    (cd build && cmake .. && make -j$(nproc))
    
    echo -e "${GREEN}All clients built successfully!${NC}"
    echo
}

# Run benchmark for each client
run_benchmark() {
    local client_name=$1
    local command=$2
    
    echo -e "${YELLOW}Running $client_name benchmark...${NC}"
    echo "Command: $command"
    echo "----------------------------------------"
    
    # Clear server stats
    curl -s http://localhost:8080/stats > /dev/null
    
    # Run the benchmark
    eval $command
    
    echo
    echo "Server-side stats:"
    curl -s http://localhost:8080/stats | python3 -m json.tool
    echo
    echo "========================================="
    echo
    
    sleep 2  # Brief pause between tests
}

# Main execution
main() {
    # Check if server is running
    if ! check_server; then
        exit 1
    fi
    
    echo
    
    # Build all clients
    build_clients
    
    echo -e "${GREEN}Starting Performance Benchmarks${NC}"
    echo "Configuration:"
    echo "  - Orders per test: $NUM_ORDERS"
    echo "  - Concurrent connections: $NUM_CONNECTIONS"
    echo "  - Warmup orders: $WARMUP"
    echo
    echo "========================================="
    echo
    
    # Run Python benchmark
    run_benchmark "Python (aiohttp)" \
        "python3 python_client.py --orders $NUM_ORDERS --connections $NUM_CONNECTIONS --warmup $WARMUP"
    
    # Run C++ benchmark
    run_benchmark "C++ (libcurl + async)" \
        "./build/cpp_client $NUM_ORDERS $NUM_CONNECTIONS $WARMUP"
    
    # Run Rust benchmark
    run_benchmark "Rust (reqwest + tokio)" \
        "./rust-client/target/release/rust-client --orders $NUM_ORDERS --connections $NUM_CONNECTIONS --warmup $WARMUP"
    
    echo -e "${GREEN}All benchmarks completed!${NC}"
    echo
    echo "Summary:"
    echo "- Python client uses aiohttp with async/await"
    echo "- C++ client uses libcurl with std::async for concurrency"
    echo "- Rust client uses reqwest with tokio async runtime"
    echo
    echo "Note: Results may vary based on system load and network conditions."
    echo "For best results, run multiple times and average the results."
}

# Run the main function
main