# Makefile for Static Library Tests

CC = gcc
AR = ar
CFLAGS = -Wall -g
ARFLAGS = rcs
LDFLAGS = -lm

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# Library name
LIB_NAME = libutils.a

# Object files
OBJS = math_utils.o string_utils.o

# Test programs
PROGRAMS = program_static1 program_static2

.PHONY: all clean test lib analysis

all: lib $(PROGRAMS)
	@echo "$(GREEN)✓$(NC) Static library and programs built"

# Build static library
lib: $(LIB_NAME)

$(LIB_NAME): $(OBJS)
	@echo "$(YELLOW)Creating static library$(NC) $@..."
	@$(AR) $(ARFLAGS) $@ $^
	@ranlib $@
	@echo "$(GREEN)✓$(NC) Static library created"

# Object files
math_utils.o: math_utils.c math_utils.h
	@echo "$(YELLOW)Compiling$(NC) $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

string_utils.o: string_utils.c string_utils.h
	@echo "$(YELLOW)Compiling$(NC) $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Test programs
program_static1: main_static.c $(LIB_NAME)
	@echo "$(YELLOW)Building$(NC) $@ (method 1: direct link)..."
	@$(CC) $(CFLAGS) $< $(LIB_NAME) $(LDFLAGS) -o $@

program_static2: main_static.c $(LIB_NAME)
	@echo "$(YELLOW)Building$(NC) $@ (method 2: -L and -l)..."
	@$(CC) $(CFLAGS) $< -L. -lutils $(LDFLAGS) -o $@

# Run tests
test: all
	@echo "$(YELLOW)=== Testing Static Library ===$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Library contents:$(NC)"
	@ar -tv $(LIB_NAME)
	@echo ""
	@echo "$(YELLOW)2. Library symbols:$(NC)"
	@nm $(LIB_NAME) | grep -E "T|D|B"
	@echo ""
	@echo "$(YELLOW)3. Running program_static1:$(NC)"
	@./program_static1
	@echo ""
	@echo "$(YELLOW)4. Checking static linking:$(NC)"
	@echo "  ldd output (should not show libutils.a):"
	@ldd program_static1 | head -5
	@echo ""
	@echo "$(YELLOW)5. Verifying embedded symbols:$(NC)"
	@nm program_static1 | grep -E "calculate_area|to_uppercase" | head -5
	@echo ""
	@echo "$(YELLOW)6. Program sizes:$(NC)"
	@ls -lh program_static*
	@echo ""
	@echo "$(GREEN)✓$(NC) Static library tests completed"

# Library analysis
analysis: $(LIB_NAME)
	@echo "$(YELLOW)=== Static Library Analysis ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Archive details:$(NC)"
	@ar -tv $(LIB_NAME)
	@echo ""
	@echo "$(YELLOW)Object file sizes:$(NC)"
	@size $(OBJS)
	@echo ""
	@echo "$(YELLOW)All symbols (demangled):$(NC)"
	@nm -C $(LIB_NAME)
	@echo ""
	@echo "$(YELLOW)Undefined symbols in library:$(NC)"
	@nm -u $(LIB_NAME) | head -10 || echo "  None"
	@echo ""
	@echo "$(YELLOW)Extract and analyze single object:$(NC)"
	@ar -x $(LIB_NAME) math_utils.o
	@file math_utils.o
	@objdump -h math_utils.o | head -15
	@rm -f math_utils.o
	@echo ""
	@echo "$(GREEN)✓$(NC) Analysis complete"

# Compare linking methods
compare: all
	@echo "$(YELLOW)=== Comparing Static Linking Methods ===$(NC)"
	@echo ""
	@echo "Method 1 (direct): program_static1"
	@size program_static1
	@echo ""
	@echo "Method 2 (-L -l): program_static2"
	@size program_static2
	@echo ""
	@echo "Binary comparison:"
	@if diff -q program_static1 program_static2 > /dev/null; then \
		echo "$(GREEN)✓$(NC) Binaries are identical"; \
	else \
		echo "$(YELLOW)!$(NC) Binaries differ (likely due to timestamps)"; \
		echo "  Checking functionality..."; \
		./program_static1 > /tmp/out1.txt 2>&1; \
		./program_static2 > /tmp/out2.txt 2>&1; \
		if diff -q /tmp/out1.txt /tmp/out2.txt > /dev/null; then \
			echo "$(GREEN)✓$(NC) But output is identical"; \
		else \
			echo "$(RED)✗$(NC) Output differs!"; \
		fi; \
	fi

# Clean build artifacts
clean:
	@echo "$(YELLOW)Cleaning static-lib...$(NC)"
	@rm -f $(OBJS) $(LIB_NAME) $(PROGRAMS) *.o
	@echo "$(GREEN)✓$(NC) Clean complete"

# Help target
help:
	@echo "Static Library Makefile Targets:"
	@echo "  make all      - Build library and test programs"
	@echo "  make lib      - Build static library only"
	@echo "  make test     - Run tests"
	@echo "  make analysis - Detailed library analysis"
	@echo "  make compare  - Compare linking methods"
	@echo "  make clean    - Remove build artifacts"