# Makefile for GDB trace demo (C and Rust)

CC = gcc
CFLAGS = -g -O0
RUSTC = rustc
RUSTFLAGS = -g -C opt-level=0 -C debuginfo=2
TARGET = demo
TARGET_RUST = demo_rust
SOURCE = demo.c
SOURCE_RUST = demo.rs
TRACE_SCRIPT = trace.py
TRACE_SCRIPT_RUST = trace_rust.py
TRACE_LOG = trace_log.txt
TRACE_LOG_RUST = rust_trace_log.txt

# Default target - build both C and Rust demos
all: $(TARGET) $(TARGET_RUST)

# Compile the C demo program
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $@ $<

# Compile the Rust demo program
$(TARGET_RUST): $(SOURCE_RUST)
	$(RUSTC) $(RUSTFLAGS) -o $@ $<

# Run C with tracing
trace: $(TARGET)
	@echo "Starting GDB trace..."
	@gdb -batch $(TARGET) \
		-ex "source $(TRACE_SCRIPT)" \
		-ex "trace-start" \
		-ex "run" \
		-ex "quit" 2>/dev/null
	@echo "Trace complete. Check $(TRACE_LOG)"

# Run with auto-trace (traces all functions)
auto-trace: $(TARGET)
	@echo "Starting GDB auto-trace..."
	@gdb -batch $(TARGET) \
		-ex "source $(TRACE_SCRIPT)" \
		-ex "auto-trace" \
		-ex "run" \
		-ex "quit" 2>/dev/null
	@echo "Auto-trace complete. Check $(TRACE_LOG)"

# Interactive GDB session with trace loaded
debug: $(TARGET)
	gdb $(TARGET) -ex "source $(TRACE_SCRIPT)"

# View the trace log
view:
	@if [ -f $(TRACE_LOG) ]; then \
		cat $(TRACE_LOG); \
	else \
		echo "No trace log found. Run 'make trace' first."; \
	fi

# Run Rust with tracing
rust-trace: $(TARGET_RUST)
	@echo "Starting Rust GDB trace..."
	@gdb -batch $(TARGET_RUST) \
		-ex "source $(TRACE_SCRIPT_RUST)" \
		-ex "rust-trace" \
		-ex "run" \
		-ex "quit" 2>/dev/null
	@echo "Rust trace complete. Check $(TRACE_LOG_RUST)"

# Run Rust auto-trace
rust-auto-trace: $(TARGET_RUST)
	@echo "Starting Rust GDB auto-trace..."
	@gdb -batch $(TARGET_RUST) \
		-ex "source $(TRACE_SCRIPT_RUST)" \
		-ex "rust-auto-trace" \
		-ex "run" \
		-ex "quit" 2>/dev/null
	@echo "Rust auto-trace complete. Check $(TRACE_LOG_RUST)"

# Interactive Rust GDB session with trace loaded
rust-debug: $(TARGET_RUST)
	gdb $(TARGET_RUST) -ex "source $(TRACE_SCRIPT_RUST)"

# Clean up
clean:
	rm -f $(TARGET) $(TARGET_RUST) *.log *.txt core

# Show help
help:
	@echo "Available targets:"
	@echo "C targets:"
	@echo "  make              - Build both C and Rust demo programs"
	@echo "  make demo         - Build C demo only"
	@echo "  make trace        - Run C with function tracing"
	@echo "  make auto-trace   - Auto-trace all C functions"
	@echo "  make debug        - Start interactive GDB with C trace loaded"
	@echo ""
	@echo "Rust targets:"
	@echo "  make demo_rust    - Build Rust demo only"
	@echo "  make rust-trace   - Run Rust with function tracing"
	@echo "  make rust-auto-trace - Auto-trace all Rust functions"
	@echo "  make rust-debug   - Start interactive GDB with Rust trace loaded"
	@echo ""
	@echo "General:"
	@echo "  make view         - View the C trace log"
	@echo "  make clean        - Remove all generated files"
	@echo "  make help         - Show this help message"

.PHONY: all trace auto-trace debug view clean help rust-trace rust-auto-trace rust-debug