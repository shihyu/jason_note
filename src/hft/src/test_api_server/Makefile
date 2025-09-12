.PHONY: all build server test clean kill-port

all: build

build:
	@echo "Building Rust API server..."
	@cd rust-api-server && cargo build --release
	@echo "Building Rust client..."
	@cd rust-client && cargo build --release
	@echo "Building C++ client..."
	@cd cpp-client && make
	@echo "Checking Python dependencies..."
	@pip install -q aiohttp tabulate

kill-port:
	@echo "Killing processes on port 8080..."
	@lsof -ti:8080 | xargs -r kill -9 2>/dev/null || true
	@echo "Port 8080 is now free"

server: kill-port
	@echo "Starting API server on port 8080..."
	@cd rust-api-server && cargo run --release

test: build
	@echo "Checking if server is running..."
	@curl -s http://localhost:8080/stats > /dev/null || (echo "Error: Server not running. Run 'make server' first" && exit 1)
	@echo "Running performance tests..."
	@python3 compare_performance.py

clean:
	@echo "Cleaning build files..."
	@cd cpp-client && make clean
	@cd rust-api-server && cargo clean
	@cd rust-client && cargo clean
	@echo "Clean complete"

help:
	@echo "Available commands:"
	@echo "  make build     - Build all components"
	@echo "  make server    - Start API server (kills existing process on port 8080)"
	@echo "  make kill-port - Kill processes using port 8080"
	@echo "  make test      - Run performance tests"
	@echo "  make clean     - Remove all build files"
	@echo "  make help      - Show this help"