.PHONY: all build server test clean python cpp rust

all: build

build: rust-server rust-client cpp python

rust-server:
	@echo "Building Rust API server..."
	@cd rust-api-server && cargo build --release

rust-client:
	@echo "Building Rust client..."
	@cd rust-client && cargo build --release

cpp:
	@echo "Building C++ client..."
	@mkdir -p build
	@cd build && cmake .. && make -j

python:
	@echo "Checking Python dependencies..."
	@pip install -q aiohttp tabulate

server:
	@echo "Starting API server on port 8080..."
	@cd rust-api-server && cargo run --release

server-background:
	@echo "Starting API server in background..."
	@cd rust-api-server && cargo run --release > /dev/null 2>&1 &
	@sleep 2
	@echo "Server started on port 8080"

test: build
	@echo "Checking if server is running..."
	@curl -s http://localhost:8080/stats > /dev/null || (echo "Error: Server not running. Run 'make server' first" && exit 1)
	@echo "Running performance tests (Python, C++, Rust)..."
	@python3 compare_performance.py

test-python:
	@python3 python_client.py --orders 1000 --connections 100

test-cpp:
	@./build/cpp_client 1000 100 100

test-rust:
	@./rust-client/target/release/rust-client --orders 1000 --connections 100

clean:
	@echo "Cleaning build files..."
	@rm -rf build
	@cd rust-api-server && cargo clean
	@cd rust-client && cargo clean
	@echo "Clean complete"

help:
	@echo "Available commands:"
	@echo "  make build    - Build all clients and server"
	@echo "  make server   - Start API server"
	@echo "  make test     - Run full performance comparison"
	@echo "  make clean    - Remove all build files"
	@echo "  make help     - Show this help message"