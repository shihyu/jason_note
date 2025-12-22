.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo "Available targets:"
	@echo "  make fix    - Fix markdown syntax issues in abseil_hints.md"
	@echo "  make check  - Verify no [code] tags or artifacts remain"
	@echo "  make test   - Alias for check"
	@echo "  make clean  - Remove temporary scripts"

.PHONY: fix
fix:  ## Fix markdown syntax issues
	python3 fix_markdown.py

.PHONY: check
check:  ## Verify no [code] tags remain
	@echo "Checking for [code] tags..."
	@if grep -q "\[code\]" abseil_hints.md; then \
		echo "FAIL: Found [code] tags"; \
		exit 1; \
	else \
		echo "PASS: No [code] tags found"; \
	fi
	@echo "Checking for web artifacts..."
	@if grep -q "Expand all details Collapse all details" abseil_hints.md; then \
		echo "FAIL: Found 'Expand all details' artifact"; \
		exit 1; \
	else \
		echo "PASS: Web artifacts removed"; \
	fi

.PHONY: test
test: check  ## Alias for check

.PHONY: clean
clean:  ## Remove temporary scripts
	rm -f fix_markdown.py
