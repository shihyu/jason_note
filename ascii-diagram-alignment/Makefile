.DEFAULT_GOAL := help

.PHONY: help build run test clean

help:
	@printf 'Targets: build (syntax and Markdown read check), run (diagram report), test (all tests), clean\n'

build:
	@python3 -c 'import ast; from pathlib import Path; files=list(Path(".").glob("*.py")); [ast.parse(p.read_text(encoding="utf-8")) for p in files]; docs=list(Path("..").rglob("*.md")); [p.read_text(encoding="utf-8") for p in docs if ".git" not in p.parts]; print(f"Validated {len(files)} Python files and {len(docs)} Markdown files")'

run:
	@python3 scan.py --root ..

test:
	@./test.sh

clean:
	@rm -rf tests/__pycache__ tests/unit/__pycache__ tests/system/__pycache__ tests/logs
