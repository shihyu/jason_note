# Buttplug.js WASM ERICA Controller Makefile
# 
# Usage:
#   make          - Build everything
#   make run      - Start development server
#   make build    - Build all components
#   make clean    - Clean build artifacts and temp files
#   make install  - Install all dependencies
#   make help     - Show this help message

.PHONY: all build run clean install help setup-wasm copy-assets dev stop

# Default target
all: build

# Show help
help:
	@echo "Buttplug.js WASM ERICA Controller"
	@echo "=================================="
	@echo "Available targets:"
	@echo "  make install  - Install all dependencies"
	@echo "  make build    - Build JS and copy WASM files"
	@echo "  make run      - Start development server (http://localhost:7777)"
	@echo "  make clean    - Clean all build artifacts"
	@echo "  make stop     - Stop development server"
	@echo ""
	@echo "Quick start:"
	@echo "  make install && make run"

# Install dependencies
install:
	@echo "Installing JS dependencies..."
	cd js && npm install --legacy-peer-deps
	@echo "Installing WASM dependencies..."
	cd wasm && npm install --legacy-peer-deps
	@echo "Installing example dependencies..."
	cd wasm/example && npm install --legacy-peer-deps
	@echo "Dependencies installed!"

# Build everything
build: copy-assets
	@echo "Build complete!"

# Build JS library (optional - skipped if dist exists)
build-js:
	@echo "Checking JS build..."
	@if [ ! -d "js/dist" ]; then \
		echo "Building JS library..."; \
		cd js && npm run build; \
		echo "JS build complete!"; \
	else \
		echo "JS dist already exists, skipping build"; \
	fi

# Ensure dependencies are installed
ensure-deps:
	@if [ ! -d "js/node_modules" ]; then \
		echo "Installing JS dependencies..."; \
		cd js && npm install --legacy-peer-deps; \
	fi
	@if [ ! -d "wasm/example/node_modules" ]; then \
		echo "Installing example dependencies..."; \
		cd wasm/example && npm install --legacy-peer-deps; \
	fi
	@if [ ! -d "js/dist" ]; then \
		echo "Building JS library..."; \
		cd js && npm run build; \
	fi

# Copy WASM assets from working example
copy-assets:
	@echo "Copying WASM assets..."
	@mkdir -p wasm/dist
	@mkdir -p wasm/example/public/wasm
	@if [ -f /home/shihyu/github/jason_note/src/web/data/buttplug-js-wasm-scan-pair-ok-features-wasm/wasm/dist/buttplug-wasm.mjs ]; then \
		cp /home/shihyu/github/jason_note/src/web/data/buttplug-js-wasm-scan-pair-ok-features-wasm/wasm/dist/*.* wasm/dist/ 2>/dev/null || true; \
	fi
	@if [ -f /home/shihyu/github/jason_note/src/web/data/buttplug-js-wasm-scan-pair-ok-features-wasm/wasm/example/public/wasm/buttplug_wasm_bg.wasm ]; then \
		cp /home/shihyu/github/jason_note/src/web/data/buttplug-js-wasm-scan-pair-ok-features-wasm/wasm/example/public/wasm/buttplug_wasm_bg.wasm wasm/example/public/wasm/; \
	fi
	@echo "Assets copied!"

# Run development server
run: stop ensure-deps build
	@echo "Starting development server..."
	@echo "=================================="
	@echo "Server will be available at:"
	@echo "  http://localhost:7777/erica.html"
	@echo "=================================="
	@echo "Press Ctrl+C to stop the server"
	@cd wasm/example && npx vite --host --port 7777

# Run in background
dev: stop build
	@echo "Starting development server in background..."
	@cd wasm/example && npx vite --host --port 7777 > /tmp/vite.log 2>&1 &
	@echo "Server started at http://localhost:7777/erica.html"
	@echo "Check logs: tail -f /tmp/vite.log"

# Stop development server
stop:
	@echo "Stopping any running Vite servers..."
	@./stop-servers.sh
	@sleep 1

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	# Clean JS build
	rm -rf js/dist
	rm -rf js/node_modules
	# Clean WASM build
	rm -rf wasm/dist
	rm -rf wasm/node_modules
	rm -rf wasm/rust/target
	rm -rf wasm/rust/pkg
	# Clean example
	rm -rf wasm/example/node_modules
	rm -rf wasm/example/dist
	rm -rf wasm/example/.vite
	# Clean test files
	rm -f wasm/example/test-*.html
	rm -f wasm/example/simple-test.html
	rm -f wasm/example/erica-discover.html
	rm -f wasm/example/erica-scan-all.html
	rm -f wasm/example/erica-working.html
	rm -f wasm/example/erica-control.html
	# Clean logs
	rm -f /tmp/vite.log
	@echo "Clean complete!"

# Deep clean (including package-lock files)
deep-clean: clean
	@echo "Deep cleaning..."
	rm -f js/package-lock.json
	rm -f wasm/package-lock.json
	rm -f wasm/example/package-lock.json
	rm -f js/yarn.lock
	rm -f wasm/yarn.lock
	rm -f wasm/example/yarn.lock
	@echo "Deep clean complete!"

# Quick test
test: build
	@echo "Opening test page..."
	@cd wasm/example && npx vite --host --port 7777 --open /erica.html