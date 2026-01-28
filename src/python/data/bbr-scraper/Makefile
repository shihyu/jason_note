# Default goal
.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo "Available targets:"
	@echo "  make build   - Install dependencies"
	@echo "  make run     - Run the scraper"
	@echo "  make test    - Run tests"
	@echo "  make clean   - Clean up output files"

.PHONY: build install
build:  ## Install dependencies
	pip install -r requirements.txt

install: build ## Alias for build

.PHONY: run
run:  ## Run the scraper
	python3 src/main.py > articles.json

.PHONY: test
test:  ## Run tests
	python3 -m unittest discover tests

.PHONY: clean
clean:  ## Clean up output files
	rm -f articles.json
	find . -type d -name "__pycache__" -exec rm -rf {} +