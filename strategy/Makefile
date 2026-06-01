.DEFAULT_GOAL := help

.PHONY: help build run test clean

DOC := Put避險與碗型底選股心法.md

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  build  Validate documentation prerequisites"
	@echo "  run    Print the generated document path"
	@echo "  test   Run all tests via ./test.sh"
	@echo "  clean  Remove test caches"

build:
	@test -d images
	@echo "Documentation workspace is ready"

run:
	@echo "$(DOC)"

test:
	@./test.sh

clean:
	@rm -rf .pytest_cache tests/**/__pycache__
	@echo "Cleaned test caches"
