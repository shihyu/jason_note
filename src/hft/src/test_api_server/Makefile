# Simple Makefile for API Performance Test
.PHONY: all build run plot clean help

# Default target
all: build

# Build all clients
build:
	@echo "Building all clients..."
	@cd c-client && make -s
	@cd cpp-client && make -s
	@cd go-client && GOARCH=amd64 GOOS=linux CGO_ENABLED=0 go build -a -ldflags="-s -w" -o go_client go_client.go
	@cd rust-client && cargo build --release --quiet
	@cd rust-api-server && cargo build --release --quiet
	@echo "✓ Build complete"

# Run performance test (alias for plot)
run: plot

# Run performance test and generate plots
plot: build
	@echo "Starting server..."
	@if [ -f server.pid ]; then kill `cat server.pid` 2>/dev/null || true; rm -f server.pid; fi
	@cd rust-api-server && ./target/release/rust-api-server > ../server.log 2>&1 & echo $$! > ../server.pid
	@sleep 2
	@echo "Running tests..."
	@python3 compare_performance.py
	@echo "✓ Test complete. Results in performance_plots/"
	@if [ -f server.pid ]; then kill `cat server.pid` 2>/dev/null || true; rm -f server.pid; fi

# Clean everything
clean:
	@echo "Cleaning..."
	@if [ -d "c-client" ]; then cd c-client && make clean -s 2>/dev/null || true; fi
	@if [ -d "cpp-client" ]; then cd cpp-client && make clean -s 2>/dev/null || true; fi
	@if [ -d "go-client" ]; then cd go-client && make clean -s 2>/dev/null || true; fi
	@if [ -d "rust-client" ]; then cd rust-client && cargo clean --quiet 2>/dev/null || true; fi
	@if [ -d "rust-api-server" ]; then cd rust-api-server && cargo clean --quiet 2>/dev/null || true; fi
	@rm -rf performance_data/ performance_plots/
	@if [ -f server.pid ]; then kill `cat server.pid` 2>/dev/null || true; fi
	@rm -f server.log server.pid
	@echo "✓ Cleaned"

# Help
help:
	@echo "Usage:"
	@echo "  make       - Build all components"
	@echo "  make run   - Run performance tests (alias for plot)"
	@echo "  make plot  - Run performance tests and generate plots"
	@echo "  make clean - Clean all files"
	@echo "  make help  - Show this help"