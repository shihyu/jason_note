.DEFAULT_GOAL := help

.PHONY: help install run run-top

help:
	@echo "Available targets:"
	@echo "  make install   - Install dependencies"
	@echo "  make run       - Run with all pairs"
	@echo "  make run-top   - Run with top 100 pairs by 1h volume"

install:
	pip install -r requirements.txt

run:
	python collect_usdt_trades.py

run-top:
	python collect_usdt_trades.py --top 100
