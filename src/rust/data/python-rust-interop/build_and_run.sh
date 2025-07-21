#!/bin/bash

echo "=== Installing dependencies ==="
pip install maturin

echo "=== Building Rust extension ==="
maturin develop

echo "=== Running Python script ==="
python main.py