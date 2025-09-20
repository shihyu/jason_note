# Makefile for API Performance Test Suite
.PHONY: all build clean plot quick-plot server stop-server help

# Default target
all: build

# Build all clients
build: build-c build-cpp build-rust-client build-rust-server
	@echo "✓ All components built successfully"

# Build individual components
build-c:
	@echo "Building C client..."
	@cd c-client && make clean && make
	@echo "✓ C client built"

build-cpp:
	@echo "Building C++ client..."
	@cd cpp-client && make clean && make
	@echo "✓ C++ client built"

build-rust-client:
	@echo "Building Rust client..."
	@cd rust-client && cargo build --release
	@echo "✓ Rust client built"

build-rust-server:
	@echo "Building Rust API server..."
	@cd rust-api-server && cargo build --release
	@echo "✓ Rust API server built"

# Start the server in background
server: build-rust-server
	@echo "Starting API server..."
	@# Kill any existing server processes
	@-pkill -f rust-api-server 2>/dev/null
	@sleep 1
	@# Start new server instance
	@echo "Starting new server instance..."
	@cd rust-api-server && nohup ./target/release/rust-api-server > ../server.log 2>&1 & echo $$! > ../server.pid
	@sleep 3
	@# Verify server started
	@if curl -s http://localhost:8080/stats > /dev/null 2>&1; then \
		echo "✓ Server started successfully"; \
	else \
		echo "✗ Failed to start server. Check server.log for details"; \
		tail -10 server.log 2>/dev/null || echo "No log file found"; \
		exit 1; \
	fi

# Stop the server
stop-server:
	@echo "Stopping API server..."
	@if [ -f server.pid ]; then \
		PID=$$(cat server.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			kill $$PID; \
			echo "✓ Server stopped (PID: $$PID)"; \
		else \
			echo "Server not running (stale PID file)"; \
		fi; \
		rm -f server.pid; \
	else \
		if pgrep -f "rust-api-server" > /dev/null 2>&1; then \
			pkill -f "rust-api-server"; \
			echo "✓ Server processes terminated"; \
		else \
			echo "No server processes found"; \
		fi; \
	fi

# Run performance comparison and generate plots
plot: build server
	@echo "Running performance comparison tests..."
	@python3 compare_performance.py
	@echo "✓ Performance plots generated in performance_plots/"

# Quick test with smaller dataset
quick-plot: build server
	@echo "Running quick performance test..."
	@python3 quick_test.py
	@echo "✓ Quick test completed with plots"

# View generated plots (Linux)
view-plots:
	@if [ -d "performance_plots" ]; then \
		if command -v xdg-open > /dev/null; then \
			xdg-open performance_plots/throughput_comparison.png 2>/dev/null; \
		elif command -v open > /dev/null; then \
			open performance_plots/throughput_comparison.png; \
		else \
			echo "Generated plots are in performance_plots/"; \
		fi \
	else \
		echo "No plots found. Run 'make plot' first."; \
	fi

# Clean everything
clean: clean-build clean-data clean-plots clean-logs
	@echo "✓ All cleaned"

# Clean build artifacts
clean-build:
	@echo "Cleaning build artifacts..."
	@cd c-client && make clean 2>/dev/null || true
	@cd cpp-client && make clean 2>/dev/null || true
	@cd rust-client && cargo clean 2>/dev/null || true
	@cd rust-api-server && cargo clean 2>/dev/null || true
	@echo "✓ Build artifacts cleaned"

# Clean generated data files
clean-data:
	@echo "Cleaning data files..."
	@rm -rf performance_data/
	@echo "✓ Data files cleaned"

# Clean generated plots
clean-plots:
	@echo "Cleaning plot files..."
	@rm -rf performance_plots/
	@echo "✓ Plot files cleaned"

# Clean log files
clean-logs:
	@echo "Cleaning log files..."
	@rm -f server.log
	@rm -f server.pid
	@rm -f *.log
	@echo "✓ Log files cleaned"

# Test individual clients
test-python: server
	@echo "Testing Python client..."
	@python3 python_client.py --orders 100 --connections 10 --warmup 10

test-c: build-c server
	@echo "Testing C client..."
	@./c-client/c_client 100 10 10

test-cpp: build-cpp server
	@echo "Testing C++ client..."
	@./cpp-client/cpp_client 100 10 10

test-rust: build-rust-client server
	@echo "Testing Rust client..."
	@./rust-client/target/release/rust-client --orders 100 --connections 10 --warmup 10

# Install Python dependencies
install-deps:
	@echo "Installing Python dependencies..."
	@pip install aiohttp tabulate
	@echo "✓ Python dependencies installed"

# Check if all dependencies are installed
check-deps:
	@echo "Checking dependencies..."
	@command -v python3 >/dev/null 2>&1 || { echo "✗ Python3 not found"; exit 1; }
	@command -v cargo >/dev/null 2>&1 || { echo "✗ Rust/Cargo not found"; exit 1; }
	@command -v gcc >/dev/null 2>&1 || { echo "✗ GCC not found"; exit 1; }
	@command -v g++ >/dev/null 2>&1 || { echo "✗ G++ not found"; exit 1; }
	@command -v gnuplot >/dev/null 2>&1 || { echo "✗ Gnuplot not found"; exit 1; }
	@command -v curl >/dev/null 2>&1 || { echo "✗ Curl not found"; exit 1; }
	@python3 -c "import aiohttp" 2>/dev/null || { echo "✗ Python aiohttp not found"; exit 1; }
	@python3 -c "import tabulate" 2>/dev/null || { echo "✗ Python tabulate not found"; exit 1; }
	@echo "✓ All dependencies installed"

# Show performance statistics
stats:
	@if [ -f "performance_data/throughput.dat" ]; then \
		echo "=== Latest Performance Results ==="; \
		cat performance_data/throughput.dat; \
		echo ""; \
		echo "=== Latency Percentiles ==="; \
		cat performance_data/latency_percentiles.dat; \
	else \
		echo "No performance data found. Run 'make plot' first."; \
	fi

# Help target
help:
	@echo "API Performance Test Suite - Makefile Targets"
	@echo "============================================="
	@echo ""
	@echo "Main targets:"
	@echo "  make build      - Build all components"
	@echo "  make plot       - Run full performance tests and generate plots"
	@echo "  make quick-plot - Run quick tests with smaller dataset"
	@echo "  make clean      - Clean all build artifacts and generated files"
	@echo ""
	@echo "Server control:"
	@echo "  make server     - Start the API server"
	@echo "  make stop-server- Stop the API server"
	@echo ""
	@echo "Individual builds:"
	@echo "  make build-c    - Build C client"
	@echo "  make build-cpp  - Build C++ client"
	@echo "  make build-rust-client - Build Rust client"
	@echo "  make build-rust-server - Build Rust server"
	@echo ""
	@echo "Testing:"
	@echo "  make test-python - Test Python client"
	@echo "  make test-c      - Test C client"
	@echo "  make test-cpp    - Test C++ client"
	@echo "  make test-rust   - Test Rust client"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean-build - Clean build artifacts only"
	@echo "  make clean-data  - Clean generated data files"
	@echo "  make clean-plots - Clean generated plots"
	@echo "  make clean-logs  - Clean log files"
	@echo ""
	@echo "Utilities:"
	@echo "  make check-deps  - Check if all dependencies are installed"
	@echo "  make install-deps- Install Python dependencies"
	@echo "  make stats       - Show latest performance statistics"
	@echo "  make view-plots  - Open generated plots (Linux/macOS)"
	@echo "  make help        - Show this help message"
