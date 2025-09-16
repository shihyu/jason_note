# Makefile for GDB trace demo

CC = gcc
CFLAGS = -g -O0
TARGET = demo
SOURCE = demo.c
TRACE_SCRIPT = trace.py
TRACE_LOG = trace_log.txt

# Default target
all: $(TARGET)

# Compile the demo program
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $@ $<

# Run with tracing
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

# Clean up
clean:
	rm -f $(TARGET) *.log *.txt core

# Show help
help:
	@echo "Available targets:"
	@echo "  make          - Build the demo program"
	@echo "  make trace    - Run with function tracing"
	@echo "  make auto-trace - Auto-trace all functions"
	@echo "  make debug    - Start interactive GDB with trace loaded"
	@echo "  make view     - View the trace log"
	@echo "  make clean    - Remove generated files"
	@echo "  make help     - Show this help message"

.PHONY: all trace auto-trace debug view clean help