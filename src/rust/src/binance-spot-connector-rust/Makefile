# Makefile for Rust project

# Define the default target
.PHONY: all
all: run_example

# Define the run_example target
.PHONY: run_example
run_example:
	cd examples && cargo run --example $(EXAMPLE_NAME)

# Allow EXAMPLE_NAME to be set from the command line or use a default value
EXAMPLE_NAME ?= tokio_tungstenite

# Add more targets as needed

