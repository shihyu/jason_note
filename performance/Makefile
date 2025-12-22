.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo "Available targets:"
	@echo "  make build  - Build the project (no-op for docs)"
	@echo "  make run    - Run/Read the documentation"
	@echo "  make test   - Verify Performance.md exists and is not empty"
	@echo "  make clean  - Clean up temporary files"

.PHONY: build
build:
	@echo "Documentation project, no build required."

.PHONY: run
run:
	@echo "Open Performance.md to read."

.PHONY: test
test:
	@if [ -s Performance.md ]; then \
		echo "PASS: Performance.md exists and is not empty."; \
	else \
		echo "FAIL: Performance.md is missing or empty."; \
		exit 1; \
	fi

.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -f *.tmp
