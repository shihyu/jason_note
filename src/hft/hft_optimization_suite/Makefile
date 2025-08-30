# HFT Optimization Suite Makefile
# Author: HFT Performance Engineering Team
# Description: Build system for hugepages, IO, and threading optimization demos

# Compiler settings
CXX = g++
CXXFLAGS = -std=c++17 -O3 -march=native -Wall -Wextra -pthread
LDFLAGS = -lrt -lpthread
DEBUG_FLAGS = -g -DDEBUG
PROFILE_FLAGS = -pg

# Color output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

# Directories
SRC_DIR = .
BUILD_DIR = build
BIN_DIR = bin

# Source files
SOURCES = hugepages_test.cpp \
          event_driven_server.cpp \
          cpu_affinity_test.cpp \
          hft_integrated_system.cpp

# Object files
OBJECTS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.o)

# Executable files
TARGETS = $(SOURCES:%.cpp=$(BIN_DIR)/%)

# Default target
.PHONY: all
all: directories $(TARGETS)
	@echo "$(GREEN)✓ Build complete!$(NC)"
	@echo "$(GREEN)Executables are in $(BIN_DIR)/$(NC)"

# Create necessary directories
.PHONY: directories
directories:
	@mkdir -p $(BUILD_DIR) $(BIN_DIR)

# Pattern rule for building executables
$(BIN_DIR)/%: $(BUILD_DIR)/%.o
	@echo "$(YELLOW)Linking $@...$(NC)"
	@$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)
	@echo "$(GREEN)✓ Built $@$(NC)"

# Pattern rule for building object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	@echo "$(YELLOW)Compiling $<...$(NC)"
	@$(CXX) $(CXXFLAGS) -c $< -o $@

# Debug build
.PHONY: debug
debug: CXXFLAGS += $(DEBUG_FLAGS)
debug: clean all
	@echo "$(GREEN)✓ Debug build complete!$(NC)"

# Profile build
.PHONY: profile
profile: CXXFLAGS += $(PROFILE_FLAGS)
profile: LDFLAGS += -pg
profile: clean all
	@echo "$(GREEN)✓ Profile build complete!$(NC)"

# Run all tests
.PHONY: test
test: all
	@echo "$(YELLOW)=== Running Test Suite ===$(NC)"
	@echo ""
	@echo "$(YELLOW)1. CPU Affinity Test$(NC)"
	@$(BIN_DIR)/cpu_affinity_test || true
	@echo ""
	@echo "$(YELLOW)2. HugePages Test (may require sudo)$(NC)"
	@$(BIN_DIR)/hugepages_test 2>/dev/null || echo "$(RED)Note: HugePages test requires system configuration$(NC)"
	@echo ""
	@echo "$(GREEN)✓ Test suite complete!$(NC)"

# Run individual tests
.PHONY: test-hugepages
test-hugepages: $(BIN_DIR)/hugepages_test
	@echo "$(YELLOW)=== HugePages Performance Test ===$(NC)"
	@sudo $(BIN_DIR)/hugepages_test || $(BIN_DIR)/hugepages_test

.PHONY: test-cpu
test-cpu: $(BIN_DIR)/cpu_affinity_test
	@echo "$(YELLOW)=== CPU Affinity Test ===$(NC)"
	@$(BIN_DIR)/cpu_affinity_test

.PHONY: test-io
test-io: $(BIN_DIR)/event_driven_server
	@echo "$(YELLOW)=== Event-Driven IO Test ===$(NC)"
	@echo "Starting server on port 8080..."
	@timeout 5 $(BIN_DIR)/event_driven_server event || true

.PHONY: test-hft
test-hft: $(BIN_DIR)/hft_integrated_system
	@echo "$(YELLOW)=== HFT Integrated System Test ===$(NC)"
	@timeout 5 $(BIN_DIR)/hft_integrated_system || true

# Benchmark suite
.PHONY: benchmark
benchmark: all
	@echo "$(YELLOW)=== Running Benchmarks ===$(NC)"
	@echo ""
	@echo "$(YELLOW)CPU Affinity Benchmark:$(NC)"
	@$(BIN_DIR)/cpu_affinity_test | grep -A 5 "CPU Affinity Test"
	@echo ""
	@echo "$(YELLOW)Memory Access Benchmark:$(NC)"
	@$(BIN_DIR)/hugepages_test | grep -A 10 "Performance Test"
	@echo ""
	@echo "$(GREEN)✓ Benchmarks complete!$(NC)"

# System setup helpers
.PHONY: setup-hugepages
setup-hugepages:
	@echo "$(YELLOW)Setting up HugePages...$(NC)"
	@echo "Current HugePage status:"
	@grep Huge /proc/meminfo || true
	@echo ""
	@echo "$(YELLOW)Configuring 512 x 2MB pages (1GB total)...$(NC)"
	@sudo sh -c 'echo 512 > /proc/sys/vm/nr_hugepages' || echo "$(RED)Failed to set hugepages (need sudo)$(NC)"
	@echo ""
	@echo "Updated HugePage status:"
	@grep Huge /proc/meminfo || true

.PHONY: setup-thp
setup-thp:
	@echo "$(YELLOW)Configuring Transparent HugePages...$(NC)"
	@cat /sys/kernel/mm/transparent_hugepage/enabled || true
	@sudo sh -c 'echo always > /sys/kernel/mm/transparent_hugepage/enabled' || echo "$(RED)Need sudo$(NC)"
	@sudo sh -c 'echo always > /sys/kernel/mm/transparent_hugepage/defrag' || echo "$(RED)Need sudo$(NC)"
	@echo "$(GREEN)✓ THP configured$(NC)"

.PHONY: system-info
system-info:
	@echo "$(YELLOW)=== System Information ===$(NC)"
	@echo "CPU Information:"
	@lscpu | grep -E "^CPU\(s\)|Thread|Core|Socket|Model name|CPU MHz"
	@echo ""
	@echo "Memory Information:"
	@free -h
	@echo ""
	@echo "HugePage Status:"
	@grep Huge /proc/meminfo || true
	@echo ""
	@echo "THP Status:"
	@cat /sys/kernel/mm/transparent_hugepage/enabled || true

# Run server and client
.PHONY: run-server
run-server: $(BIN_DIR)/event_driven_server
	@echo "$(YELLOW)Starting Event-Driven Server on port 8080...$(NC)"
	@$(BIN_DIR)/event_driven_server event

.PHONY: run-client
run-client: $(BIN_DIR)/event_driven_server
	@echo "$(YELLOW)Starting Load Test Client...$(NC)"
	@$(BIN_DIR)/event_driven_server test

.PHONY: run-hft
run-hft: $(BIN_DIR)/hft_integrated_system
	@echo "$(YELLOW)Starting HFT System...$(NC)"
	@$(BIN_DIR)/hft_integrated_system

# Performance monitoring
.PHONY: perf-monitor
perf-monitor:
	@echo "$(YELLOW)=== Performance Monitoring ===$(NC)"
	@echo "TLB Statistics:"
	@perf stat -e dTLB-loads,dTLB-load-misses,iTLB-loads,iTLB-load-misses sleep 1 2>&1 | grep -E "TLB|seconds" || echo "perf not available"
	@echo ""
	@echo "Context Switches:"
	@vmstat 1 3

# Clean build artifacts
.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "$(GREEN)✓ Clean complete!$(NC)"

# Clean everything including generated files
.PHONY: distclean
distclean: clean
	@echo "$(YELLOW)Removing all generated files...$(NC)"
	@rm -f *.o *.out core.* perf.data* gmon.out
	@echo "$(GREEN)✓ Distribution clean complete!$(NC)"

# Help target
.PHONY: help
help:
	@echo "$(YELLOW)=== HFT Optimization Suite Makefile ===$(NC)"
	@echo ""
	@echo "$(GREEN)Build Targets:$(NC)"
	@echo "  make all          - Build all programs"
	@echo "  make debug        - Build with debug symbols"
	@echo "  make profile      - Build with profiling support"
	@echo ""
	@echo "$(GREEN)Test Targets:$(NC)"
	@echo "  make test         - Run all tests"
	@echo "  make test-hugepages - Test hugepages performance"
	@echo "  make test-cpu     - Test CPU affinity"
	@echo "  make test-io      - Test event-driven IO"
	@echo "  make test-hft     - Test integrated HFT system"
	@echo "  make benchmark    - Run benchmark suite"
	@echo ""
	@echo "$(GREEN)System Setup:$(NC)"
	@echo "  make setup-hugepages - Configure system hugepages"
	@echo "  make setup-thp    - Configure transparent hugepages"
	@echo "  make system-info  - Display system information"
	@echo ""
	@echo "$(GREEN)Run Programs:$(NC)"
	@echo "  make run-server   - Run event-driven server"
	@echo "  make run-client   - Run load test client"
	@echo "  make run-hft      - Run HFT system"
	@echo ""
	@echo "$(GREEN)Maintenance:$(NC)"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make distclean    - Remove all generated files"
	@echo "  make perf-monitor - Monitor system performance"
	@echo ""
	@echo "$(YELLOW)Note: Some operations require sudo privileges$(NC)"

# Check dependencies
.PHONY: check-deps
check-deps:
	@echo "$(YELLOW)=== Checking Dependencies ===$(NC)"
	@which g++ > /dev/null && echo "$(GREEN)✓ g++ found$(NC)" || echo "$(RED)✗ g++ not found$(NC)"
	@which perf > /dev/null 2>&1 && echo "$(GREEN)✓ perf found$(NC)" || echo "$(YELLOW)⚠ perf not found (optional)$(NC)"
	@which vmstat > /dev/null && echo "$(GREEN)✓ vmstat found$(NC)" || echo "$(YELLOW)⚠ vmstat not found (optional)$(NC)"
	@echo ""
	@echo "Checking CPU features:"
	@grep -q pse /proc/cpuinfo && echo "$(GREEN)✓ 2MB pages supported$(NC)" || echo "$(RED)✗ 2MB pages not supported$(NC)"
	@grep -q pdpe1gb /proc/cpuinfo && echo "$(GREEN)✓ 1GB pages supported$(NC)" || echo "$(YELLOW)⚠ 1GB pages not supported$(NC)"

# Default help if no target specified
.DEFAULT_GOAL := help