# SPDX-License-Identifier: BSD-3-Clause
# Copyright(c) 2010-2020 Intel Corporation

# DPDK Test Program Makefile

# Compiler and flags
CC = gcc
CFLAGS = -g -O0 -march=native

# DPDK paths
DPDK_BUILD = ./build
DPDK_INCLUDES = \
    -I$(DPDK_BUILD)/include \
    -I./lib/eal/include \
    -I./lib/eal/x86/include \
    -I./lib/eal/linux/include \
    -I./lib/eal/common \
    -I./lib/ethdev \
    -I./lib/net \
    -I./lib/mbuf \
    -I./lib/mempool \
    -I./lib/ring \
    -I./lib/meter \
    -I./lib/metrics \
    -I./lib/telemetry \
    -I./lib/kvargs \
    -I./lib/log \
    -I./config \
    -I$(DPDK_BUILD)

# DPDK libraries
DPDK_LIBS = \
    -L$(DPDK_BUILD)/lib \
    -Wl,--whole-archive \
    -lrte_eal -lrte_ethdev -lrte_mbuf -lrte_mempool \
    -lrte_ring -lrte_net -lrte_meter -lrte_telemetry \
    -lrte_kvargs -lrte_log \
    -Wl,--no-whole-archive \
    -lpthread -ldl -lnuma

# Target executable
TARGET = $(DPDK_BUILD)/test_dpdk

# Source files
SRCS = test_dpdk.c

# Default target
.PHONY: all
all: dpdk test_dpdk

# Build DPDK
.PHONY: dpdk
dpdk:
	@echo "Building DPDK..."
	@if [ ! -d "$(DPDK_BUILD)" ]; then \
		echo "Configuring DPDK build with debug symbols..."; \
		meson setup $(DPDK_BUILD) --buildtype=debug; \
	fi
	@ninja -C $(DPDK_BUILD) -j$$(nproc)
	@echo "DPDK build completed."

# Build test program
.PHONY: test_dpdk
test_dpdk: $(TARGET)

$(TARGET): $(SRCS) | dpdk
	@echo "Building test_dpdk..."
	$(CC) -o $@ $< $(DPDK_INCLUDES) $(DPDK_LIBS) $(CFLAGS)
	@echo "test_dpdk build completed: $@"

# Run with GDB
.PHONY: debug
debug: $(TARGET)
	@echo "Starting GDB debugger..."
	@chmod +x run_dpdk_gdb.sh 2>/dev/null || true
	@./run_dpdk_gdb.sh

# Run in QEMU
.PHONY: qemu
qemu: $(TARGET)
	@echo "Starting QEMU..."
	@chmod +x run_qemu_dpdk.sh 2>/dev/null || true
	@./run_qemu_dpdk.sh

# Clean DPDK build
.PHONY: clean-dpdk
clean-dpdk:
	@echo "Cleaning DPDK build..."
	@if [ -d "$(DPDK_BUILD)" ]; then \
		ninja -C $(DPDK_BUILD) clean; \
	fi

# Clean test program only
.PHONY: clean-test
clean-test:
	@echo "Cleaning test program..."
	@rm -f $(TARGET)

# Clean everything
.PHONY: clean
clean:
	@echo "Cleaning all build artifacts..."
	@if [ -d "$(DPDK_BUILD)" ]; then \
		rm -rf $(DPDK_BUILD); \
	fi
	@echo "Clean completed."

# Clean and rebuild
.PHONY: rebuild
rebuild: clean all

# Setup system environment
.PHONY: setup
setup:
	@echo "Setting up system environment..."
	@echo "Setting hugepages..."
	@echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
	@echo "Loading kernel modules..."
	@sudo modprobe vfio-pci
	@echo "Setting library path..."
	@export LD_LIBRARY_PATH=$(DPDK_BUILD)/lib:$$LD_LIBRARY_PATH
	@echo "Setup completed."

# Cleanup system environment
.PHONY: cleanup
cleanup:
	@echo "Cleaning up system environment..."
	@echo "Removing TAP interface if exists..."
	@sudo ip link del tap0 2>/dev/null || true
	@echo "Releasing hugepages..."
	@echo 0 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
	@echo "Cleanup completed."

# Show help
.PHONY: help
help:
	@echo "DPDK Test Program Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all         - Build DPDK and test program (default)"
	@echo "  dpdk        - Build DPDK only"
	@echo "  test_dpdk   - Build test program only"
	@echo "  debug       - Run test program with GDB"
	@echo "  qemu        - Run test program in QEMU"
	@echo "  clean       - Remove all build artifacts"
	@echo "  clean-dpdk  - Clean DPDK build only"
	@echo "  clean-test  - Clean test program only"
	@echo "  rebuild     - Clean and rebuild everything"
	@echo "  setup       - Setup system environment (hugepages, modules)"
	@echo "  cleanup     - Cleanup system environment"
	@echo "  help        - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make                # Build everything"
	@echo "  make clean          # Clean everything"
	@echo "  make debug          # Run with GDB"
	@echo "  make qemu           # Run in QEMU"
