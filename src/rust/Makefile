.DEFAULT_GOAL := help

.PHONY: help build run test clean

help:
	@printf 'Targets: build (UTF-8 check), run (diagram scan), test (all tests), clean\n'

build:
	@python3 -c 'from pathlib import Path; files = list(Path(".").rglob("*.md")); [path.read_text(encoding="utf-8") for path in files]; print(f"Validated {len(files)} Markdown files as UTF-8")'

run:
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/system -v

test:
	@./test.sh

clean:
	@rm -rf tests/__pycache__ tests/system/__pycache__ tests/unit/__pycache__
