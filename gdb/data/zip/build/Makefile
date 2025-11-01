# Makefile for building and debugging zip tools
# Usage:
#   make           - Build debug executables
#   make debug     - Run GDB trace
#   make test      - Build and run debug trace
#   make clean     - Clean all generated files

# Directories
SRC_DIR = ../src
BUILD_DIR = .
TEST_FILE = test.txt

# Compiler settings
CC = gcc
CFLAGS = -g -O0 -Wall -D_GNU_SOURCE

# Source files
COMMON_SRCS = $(SRC_DIR)/miniz.c $(SRC_DIR)/zip.c $(SRC_DIR)/unixutils.c
ZIP_SRC = $(SRC_DIR)/tools/cmdzip.c
UNZIP_SRC = $(SRC_DIR)/tools/cmdunzip.c

# Output executables
ZIP_DEBUG = cmdzip_debug
UNZIP_DEBUG = cmdunzip_debug

# Default target
.PHONY: all
all: $(ZIP_DEBUG) $(UNZIP_DEBUG)
	@echo ""
	@echo "=== Build completed ==="
	@echo "Debug executables:"
	@echo "  - $(BUILD_DIR)/$(ZIP_DEBUG)"
	@echo "  - $(BUILD_DIR)/$(UNZIP_DEBUG)"
	@echo ""
	@echo "Usage:"
	@echo "  make trace   - Trace function execution path"
	@echo "  make debug   - Run GDB trace"
	@echo "  make test    - Build and run debug trace"
	@echo "  make clean   - Clean generated files"

# Build cmdzip_debug
$(ZIP_DEBUG): $(COMMON_SRCS) $(ZIP_SRC)
	@echo "Building $(ZIP_DEBUG)..."
	$(CC) $(CFLAGS) $(COMMON_SRCS) $(ZIP_SRC) -o $(ZIP_DEBUG)
	@file $(ZIP_DEBUG) | grep -q "with debug_info" && echo "✓ $(ZIP_DEBUG) built with debug symbols"

# Build cmdunzip_debug
$(UNZIP_DEBUG): $(COMMON_SRCS) $(UNZIP_SRC)
	@echo "Building $(UNZIP_DEBUG)..."
	$(CC) $(CFLAGS) $(COMMON_SRCS) $(UNZIP_SRC) -o $(UNZIP_DEBUG)
	@file $(UNZIP_DEBUG) | grep -q "with debug_info" && echo "✓ $(UNZIP_DEBUG) built with debug symbols"

# Prepare test data
.PHONY: prepare
prepare:
	@echo "=== Preparing test data ==="
	@echo "Creating test file..."
	@echo "Hello, this is a test file for zip compression." > $(TEST_FILE)
	@echo "This file will be used to trace the zip process with GDB." >> $(TEST_FILE)
	@echo "Line 3: Testing compression functionality." >> $(TEST_FILE)
	@echo "Line 4: Debugging with GDB is powerful!" >> $(TEST_FILE)
	@echo "✓ Test file created: $(TEST_FILE)"
	@echo ""
	@echo "Creating zip input data..."
	@python3 -c 'import struct; \
	num_files = 1; \
	keys = ["test.txt"]; \
	files = ["$(TEST_FILE)"]; \
	dirs = [0]; \
	mtimes = [float(1234567890)]; \
	f = open("zip_input.bin", "wb"); \
	f.write(struct.pack("i", num_files)); \
	keys_buffer = "\0".join(keys) + "\0"; \
	f.write(struct.pack("i", len(keys_buffer))); \
	f.write(keys_buffer.encode("utf-8")); \
	files_buffer = "\0".join(files) + "\0"; \
	f.write(struct.pack("i", len(files_buffer))); \
	f.write(files_buffer.encode("utf-8")); \
	[f.write(struct.pack("i", d)) for d in dirs]; \
	[f.write(struct.pack("d", mt)) for mt in mtimes]; \
	f.close(); \
	print("✓ zip_input.bin created")'

# Run GDB trace (detailed)
.PHONY: debug
debug: $(ZIP_DEBUG) prepare
	@echo ""
	@echo "=== Running GDB trace ==="
	@echo ""
	@gdb -batch -x gdb_trace.gdb --args ./$(ZIP_DEBUG) output.zip zip_input.bin
	@echo ""
	@if [ -f output.zip ]; then \
		echo "=== Compression successful ==="; \
		ls -lh output.zip; \
		echo ""; \
		echo "Verifying zip contents:"; \
		unzip -l output.zip; \
	else \
		echo "=== Compression failed ==="; \
	fi
	@echo ""
	@echo "=== Trace completed ==="

# Run function trace (execution path only)
.PHONY: trace
trace: $(ZIP_DEBUG) prepare
	@echo ""
	@echo "=== Function Execution Trace ==="
	@echo ""
	@gdb -batch -x gdb_function_trace.gdb --args ./$(ZIP_DEBUG) output.zip zip_input.bin
	@echo ""
	@if [ -f output.zip ]; then \
		echo "=== Compression successful ==="; \
		ls -lh output.zip; \
		unzip -l output.zip; \
	fi

# Interactive GDB
.PHONY: gdb
gdb: $(ZIP_DEBUG) prepare
	@echo "Starting interactive GDB..."
	@echo "Suggested commands:"
	@echo "  (gdb) break main"
	@echo "  (gdb) break zip_zip"
	@echo "  (gdb) run"
	@echo ""
	gdb --args ./$(ZIP_DEBUG) output.zip zip_input.bin

# Build and test
.PHONY: test
test: debug

# Clean
.PHONY: clean
clean:
	@echo "Cleaning generated files..."
	rm -f $(ZIP_DEBUG) $(UNZIP_DEBUG)
	rm -f $(TEST_FILE) zip_input.bin output.zip test.log
	@echo "✓ Clean completed"

# Help
.PHONY: help
help:
	@echo "Makefile for zip debugging"
	@echo ""
	@echo "Targets:"
	@echo "  make           - Build debug executables"
	@echo "  make trace     - Trace function execution path"
	@echo "  make debug     - Run automated GDB trace"
	@echo "  make gdb       - Start interactive GDB session"
	@echo "  make test      - Build and run debug trace"
	@echo "  make prepare   - Prepare test data only"
	@echo "  make clean     - Clean all generated files"
	@echo "  make help      - Show this help message"
