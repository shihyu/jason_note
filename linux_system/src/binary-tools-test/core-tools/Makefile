# Makefile for Core Binary Tools Tests

CC = gcc
CFLAGS = -g -O0 -Wall
LDFLAGS = -lm

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# Targets
TARGETS = simple_test perf_test perf_test_gprof mem_test

.PHONY: all clean test analysis

all: $(TARGETS)
	@echo "$(GREEN)✓$(NC) Core tools binaries built"

# Simple test program
simple_test: simple_test.c
	@echo "$(YELLOW)Building$(NC) $@..."
	@$(CC) $(CFLAGS) -o $@ $<

# Performance test program
perf_test: perf_test.c
	@echo "$(YELLOW)Building$(NC) $@..."
	@$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Performance test with gprof
perf_test_gprof: perf_test.c
	@echo "$(YELLOW)Building$(NC) $@ (with profiling)..."
	@$(CC) -pg $(CFLAGS) -o $@ $< $(LDFLAGS)

# Memory test program
mem_test: mem_test.c
	@echo "$(YELLOW)Building$(NC) $@..."
	@$(CC) $(CFLAGS) -o $@ $<

# Create test C files if they don't exist
perf_test.c:
	@echo "Creating perf_test.c..."
	@echo '#include <stdio.h>' > $@
	@echo '#include <math.h>' >> $@
	@echo '#include <stdlib.h>' >> $@
	@echo '' >> $@
	@echo 'double compute_intensive(int n) {' >> $@
	@echo '    double sum = 0;' >> $@
	@echo '    for (int i = 0; i < n; i++) {' >> $@
	@echo '        sum += sqrt(i) * sin(i);' >> $@
	@echo '    }' >> $@
	@echo '    return sum;' >> $@
	@echo '}' >> $@
	@echo '' >> $@
	@echo 'int main() {' >> $@
	@echo '    printf("Starting performance test...\\n");' >> $@
	@echo '    for (int i = 0; i < 5; i++) {' >> $@
	@echo '        double result = compute_intensive(1000000);' >> $@
	@echo '        printf("Iteration %d: %f\\n", i, result);' >> $@
	@echo '    }' >> $@
	@echo '    return 0;' >> $@
	@echo '}' >> $@

mem_test.c:
	@echo "Creating mem_test.c..."
	@echo '#include <stdlib.h>' > $@
	@echo '#include <string.h>' >> $@
	@echo '' >> $@
	@echo 'int main() {' >> $@
	@echo '    char *buffer = malloc(100);' >> $@
	@echo '    strcpy(buffer, "Hello");' >> $@
	@echo '    /* Intentional memory leak - not freeing buffer */' >> $@
	@echo '    return 0;' >> $@
	@echo '}' >> $@

# Run tests
test: all
	@echo "$(YELLOW)=== Testing Core Binary Tools ===$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Testing nm:$(NC)"
	@nm simple_test | head -5
	@echo ""
	@echo "$(YELLOW)2. Testing objdump:$(NC)"
	@objdump -d simple_test | grep -A5 "<main>:" | head -10
	@echo ""
	@echo "$(YELLOW)3. Testing readelf:$(NC)"
	@readelf -h simple_test | head -5
	@echo ""
	@echo "$(YELLOW)4. Testing strings:$(NC)"
	@strings simple_test | grep -E "Hello|function" | head -3
	@echo ""
	@echo "$(YELLOW)5. Testing file:$(NC)"
	@file simple_test
	@echo ""
	@echo "$(YELLOW)6. Testing size:$(NC)"
	@size simple_test
	@echo ""
	@echo "$(YELLOW)7. Testing ldd:$(NC)"
	@ldd simple_test | head -5
	@echo ""
	@echo "$(GREEN)✓$(NC) Core tools tests completed"

# Advanced analysis
analysis: all
	@echo "$(YELLOW)=== Advanced Binary Analysis ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Symbol Analysis:$(NC)"
	@nm -C simple_test | grep -E "global_|weak_|static_" || true
	@echo ""
	@echo "$(YELLOW)Section Headers:$(NC)"
	@objdump -h simple_test | head -15
	@echo ""
	@echo "$(YELLOW)Dynamic Dependencies:$(NC)"
	@readelf -d simple_test | grep NEEDED
	@echo ""
	@echo "$(YELLOW)Security Features:$(NC)"
	@echo -n "  RELRO: "; readelf -l simple_test | grep -q GNU_RELRO && echo "$(GREEN)Yes$(NC)" || echo "$(RED)No$(NC)"
	@echo -n "  Stack Canary: "; nm simple_test | grep -q __stack_chk && echo "$(GREEN)Yes$(NC)" || echo "$(RED)No$(NC)"
	@echo -n "  PIE: "; readelf -h simple_test | grep -q "DYN" && echo "$(GREEN)Yes$(NC)" || echo "$(RED)No$(NC)"
	@echo ""
	@echo "$(GREEN)✓$(NC) Analysis complete"

# Performance profiling
profile: perf_test_gprof
	@echo "$(YELLOW)Running profiling test...$(NC)"
	@./perf_test_gprof > /dev/null
	@if [ -f gmon.out ]; then \
		echo "$(YELLOW)Generating profile report:$(NC)"; \
		gprof perf_test_gprof gmon.out | head -30; \
	else \
		echo "$(RED)gmon.out not generated$(NC)"; \
	fi

# Debug with strace
trace: simple_test
	@echo "$(YELLOW)System call trace (first 20 lines):$(NC)"
	@strace -e trace=file ./simple_test 2>&1 | head -20

# Clean build artifacts
clean:
	@echo "$(YELLOW)Cleaning core-tools...$(NC)"
	@rm -f $(TARGETS) *.o gmon.out perf_test.c mem_test.c
	@echo "$(GREEN)✓$(NC) Clean complete"

# Help target
help:
	@echo "Core Tools Makefile Targets:"
	@echo "  make all      - Build all test programs"
	@echo "  make test     - Run basic tool tests"
	@echo "  make analysis - Run advanced analysis"
	@echo "  make profile  - Run performance profiling"
	@echo "  make trace    - Trace system calls"
	@echo "  make clean    - Remove build artifacts"