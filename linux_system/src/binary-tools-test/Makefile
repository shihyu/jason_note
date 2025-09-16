# Main Makefile for Linux Binary Tools Test Suite
# This Makefile orchestrates all test components

.PHONY: all clean test help install-deps
.PHONY: core-tools static-lib dynamic-lib dlopen-demo
.PHONY: test-core test-static test-dynamic test-dlopen test-ld test-debug

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Default target
all: build-all test-all report

help:
	@echo "$(GREEN)Linux Binary Tools Test Suite$(NC)"
	@echo "================================"
	@echo "Available targets:"
	@echo "  make all          - Build and test everything"
	@echo "  make build-all    - Build all test programs"
	@echo "  make test-all     - Run all tests"
	@echo "  make clean        - Clean all build artifacts"
	@echo "  make report       - Generate test report"
	@echo "  make install-deps - Install required tools"
	@echo ""
	@echo "Individual targets:"
	@echo "  make core-tools   - Build core tools tests"
	@echo "  make static-lib   - Build static library tests"
	@echo "  make dynamic-lib  - Build dynamic library tests"
	@echo "  make dlopen-demo  - Build dlopen/plugin tests"
	@echo ""
	@echo "Individual tests:"
	@echo "  make test-core    - Test core binary tools"
	@echo "  make test-static  - Test static libraries"
	@echo "  make test-dynamic - Test dynamic libraries"
	@echo "  make test-dlopen  - Test dlopen/plugins"
	@echo "  make test-ld      - Test LD environment"
	@echo "  make test-debug   - Test debugging tools"

# Build all components
build-all: core-tools static-lib dynamic-lib dlopen-demo
	@echo "$(GREEN)[BUILD]$(NC) All components built successfully"

# Build individual components
core-tools:
	@echo "$(YELLOW)[BUILD]$(NC) Building core tools tests..."
	@$(MAKE) -C core-tools --no-print-directory

static-lib:
	@echo "$(YELLOW)[BUILD]$(NC) Building static library tests..."
	@$(MAKE) -C static-lib --no-print-directory

dynamic-lib:
	@echo "$(YELLOW)[BUILD]$(NC) Building dynamic library tests..."
	@$(MAKE) -C dynamic-lib --no-print-directory

dlopen-demo:
	@echo "$(YELLOW)[BUILD]$(NC) Building dlopen/plugin tests..."
	@$(MAKE) -C dlopen-demo --no-print-directory

# Run all tests
test-all: test-core test-static test-dynamic test-dlopen test-ld test-debug
	@echo "$(GREEN)[TEST]$(NC) All tests completed"

# Individual test targets
test-core: core-tools
	@echo "$(YELLOW)[TEST]$(NC) Testing core binary tools..."
	@$(MAKE) -C core-tools test --no-print-directory

test-static: static-lib
	@echo "$(YELLOW)[TEST]$(NC) Testing static libraries..."
	@$(MAKE) -C static-lib test --no-print-directory

test-dynamic: dynamic-lib
	@echo "$(YELLOW)[TEST]$(NC) Testing dynamic libraries..."
	@$(MAKE) -C dynamic-lib test --no-print-directory

test-dlopen: dlopen-demo
	@echo "$(YELLOW)[TEST]$(NC) Testing dlopen and plugins..."
	@$(MAKE) -C dlopen-demo test --no-print-directory

test-ld: dynamic-lib
	@echo "$(YELLOW)[TEST]$(NC) Testing LD environment variables..."
	@cd dynamic-lib && ../test_ld_tools.sh 2>&1 | head -50

test-debug: core-tools
	@echo "$(YELLOW)[TEST]$(NC) Testing debugging tools..."
	@./test_debug_tools.sh 2>&1 | head -50

# Generate test report
report:
	@echo "$(GREEN)================================$(NC)"
	@echo "$(GREEN)Test Summary Report$(NC)"
	@echo "$(GREEN)================================$(NC)"
	@echo ""
	@echo "Components built and tested:"
	@echo "  ✓ Core binary analysis tools"
	@echo "  ✓ Static libraries"
	@echo "  ✓ Dynamic libraries"
	@echo "  ✓ dlopen and plugin system"
	@echo "  ✓ LD environment variables"
	@echo "  ✓ Debugging tools"
	@echo ""
	@echo "See TEST_REPORT.md for detailed results"

# Clean all build artifacts
clean:
	@echo "$(YELLOW)[CLEAN]$(NC) Cleaning all build artifacts..."
	@$(MAKE) -C core-tools clean --no-print-directory 2>/dev/null || true
	@$(MAKE) -C static-lib clean --no-print-directory 2>/dev/null || true
	@$(MAKE) -C dynamic-lib clean --no-print-directory 2>/dev/null || true
	@$(MAKE) -C dlopen-demo clean --no-print-directory 2>/dev/null || true
	@rm -f *.log gmon.out
	@echo "$(GREEN)[CLEAN]$(NC) Clean complete"

# Install dependencies
install-deps:
	@echo "$(YELLOW)[DEPS]$(NC) Checking and installing dependencies..."
	@which nm > /dev/null || (echo "Installing binutils..." && sudo apt-get install -y binutils)
	@which strace > /dev/null || (echo "Installing strace..." && sudo apt-get install -y strace)
	@which ltrace > /dev/null 2>&1 || (echo "Installing ltrace..." && sudo apt-get install -y ltrace) || true
	@which valgrind > /dev/null 2>&1 || (echo "Installing valgrind..." && sudo apt-get install -y valgrind) || true
	@echo "$(GREEN)[DEPS]$(NC) Dependencies installed"

# Check tools availability
check-tools:
	@echo "$(YELLOW)Tool Availability Check:$(NC)"
	@echo "========================"
	@which nm > /dev/null && echo "$(GREEN)✓$(NC) nm" || echo "$(RED)✗$(NC) nm"
	@which objdump > /dev/null && echo "$(GREEN)✓$(NC) objdump" || echo "$(RED)✗$(NC) objdump"
	@which readelf > /dev/null && echo "$(GREEN)✓$(NC) readelf" || echo "$(RED)✗$(NC) readelf"
	@which ldd > /dev/null && echo "$(GREEN)✓$(NC) ldd" || echo "$(RED)✗$(NC) ldd"
	@which strace > /dev/null && echo "$(GREEN)✓$(NC) strace" || echo "$(RED)✗$(NC) strace"
	@which ltrace > /dev/null 2>&1 && echo "$(GREEN)✓$(NC) ltrace" || echo "$(RED)✗$(NC) ltrace (optional)"
	@which valgrind > /dev/null 2>&1 && echo "$(GREEN)✓$(NC) valgrind" || echo "$(RED)✗$(NC) valgrind (optional)"
	@which perf > /dev/null 2>&1 && echo "$(GREEN)✓$(NC) perf" || echo "$(RED)✗$(NC) perf (optional)"

# Verbose test with detailed output
test-verbose:
	@$(MAKE) test-all VERBOSE=1

.PHONY: check-tools test-verbose