# Makefile for dlopen and Plugin System Tests

CC = gcc
CFLAGS = -Wall -g
PLUGIN_CFLAGS = -fPIC -fvisibility=hidden
LDFLAGS = -ldl
PLUGIN_LDFLAGS = -shared

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# Plugin directory
PLUGIN_DIR = plugins

# Main programs
PROGRAMS = dlopen_demo dlopen_simple plugin_loader dlopen_advanced

# Plugin libraries
PLUGINS = $(PLUGIN_DIR)/plugin1.so $(PLUGIN_DIR)/plugin2.so

# Dynamic library from parent directory
PARENT_LIB = libdynamic.so

.PHONY: all clean test plugins analysis advanced-test

all: prepare $(PROGRAMS) plugins
	@echo "$(GREEN)✓$(NC) dlopen demos and plugins built"

# Prepare environment
prepare:
	@mkdir -p $(PLUGIN_DIR)
	@if [ ! -f $(PARENT_LIB) ]; then \
		echo "$(YELLOW)Copying dynamic library from parent...$(NC)"; \
		cp ../dynamic-lib/$(PARENT_LIB) . 2>/dev/null || \
		(cd ../dynamic-lib && make libdynamic.so && cp libdynamic.so ../dlopen-demo/) || \
		echo "$(RED)Warning: Could not get libdynamic.so$(NC)"; \
	fi

# Main programs
dlopen_demo: dlopen_demo.c
	@echo "$(YELLOW)Building$(NC) $@..."
	@$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

dlopen_simple: dlopen_simple.c
	@echo "$(YELLOW)Building$(NC) $@..."
	@$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

plugin_loader: plugin_loader.c plugin_interface.h
	@echo "$(YELLOW)Building$(NC) $@..."
	@$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

dlopen_advanced: dlopen_advanced.c
	@echo "$(YELLOW)Building$(NC) $@..."
	@$(CC) $(CFLAGS) -D_GNU_SOURCE -o $@ $< $(LDFLAGS)

# Build all plugins
plugins: $(PLUGINS)
	@echo "$(GREEN)✓$(NC) Plugins built"

$(PLUGIN_DIR)/plugin1.so: plugin1.c plugin_interface.h
	@echo "$(YELLOW)Building plugin$(NC) $@..."
	@$(CC) $(PLUGIN_CFLAGS) $(PLUGIN_LDFLAGS) -o $@ $<

$(PLUGIN_DIR)/plugin2.so: plugin2.c plugin_interface.h
	@echo "$(YELLOW)Building plugin$(NC) $@..."
	@$(CC) $(PLUGIN_CFLAGS) $(PLUGIN_LDFLAGS) -o $@ $<

# Run tests
test: all
	@echo "$(YELLOW)=== Testing dlopen and Plugin System ===$(NC)"
	@echo ""
	@if [ -f $(PARENT_LIB) ]; then \
		echo "$(YELLOW)1. Basic dlopen test:$(NC)"; \
		./dlopen_demo; \
		echo ""; \
	else \
		echo "$(RED)Skipping dlopen_demo (libdynamic.so not found)$(NC)"; \
		echo ""; \
	fi
	@echo "$(YELLOW)2. Simple dlopen test:$(NC)"
	@./dlopen_simple
	@echo ""
	@echo "$(YELLOW)3. Plugin system test:$(NC)"
	@./plugin_loader
	@echo ""
	@echo "$(YELLOW)4. Plugin symbols check:$(NC)"
	@echo "  Plugin 1:"
	@nm -D $(PLUGIN_DIR)/plugin1.so | grep plugin_info || echo "    No symbols"
	@echo "  Plugin 2:"
	@nm -D $(PLUGIN_DIR)/plugin2.so | grep plugin_info || echo "    No symbols"
	@echo ""
	@echo "$(YELLOW)5. Advanced dlopen features:$(NC)"
	@./dlopen_advanced 2>/dev/null || echo "  Some features may not be available"
	@echo ""
	@echo "$(GREEN)✓$(NC) dlopen tests completed"

# Detailed analysis
analysis: plugins
	@echo "$(YELLOW)=== Plugin System Analysis ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Plugin structure:$(NC)"
	@ls -la $(PLUGIN_DIR)/
	@echo ""
	@echo "$(YELLOW)Plugin 1 details:$(NC)"
	@file $(PLUGIN_DIR)/plugin1.so
	@readelf -d $(PLUGIN_DIR)/plugin1.so | grep -E "NEEDED|SONAME"
	@echo ""
	@echo "$(YELLOW)Plugin 2 details:$(NC)"
	@file $(PLUGIN_DIR)/plugin2.so
	@readelf -d $(PLUGIN_DIR)/plugin2.so | grep -E "NEEDED|SONAME"
	@echo ""
	@echo "$(YELLOW)Exported symbols in plugins:$(NC)"
	@for plugin in $(PLUGINS); do \
		echo "  $$plugin:"; \
		nm -D $$plugin 2>/dev/null | grep -v "^$$" || echo "    No dynamic symbols"; \
	done
	@echo ""
	@echo "$(GREEN)✓$(NC) Analysis complete"

# Advanced dlopen testing
advanced-test: dlopen_advanced
	@echo "$(YELLOW)=== Advanced dlopen Features ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Testing dlopen flags and dladdr:$(NC)"
	@./dlopen_advanced
	@echo ""
	@echo "$(YELLOW)Testing RTLD flags with LD_DEBUG:$(NC)"
	@LD_DEBUG=symbols ./dlopen_simple 2>&1 | grep dlopen | head -5
	@echo ""
	@echo "$(YELLOW)Library loading trace:$(NC)"
	@strace -e openat ./dlopen_simple 2>&1 | grep "\.so" | head -10
	@echo ""
	@echo "$(GREEN)✓$(NC) Advanced tests complete"

# Plugin development test
plugin-dev: plugins plugin_loader
	@echo "$(YELLOW)=== Plugin Development Test ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Creating new test plugin...$(NC)"
	@echo '#include "plugin_interface.h"' > plugin_test.c
	@echo '#include <stdio.h>' >> plugin_test.c
	@echo 'static int test_init() { printf("Test plugin init\\n"); return 0; }' >> plugin_test.c
	@echo 'static int test_exec(const char *a) { printf("Test exec: %s\\n", a?a:"null"); return 0; }' >> plugin_test.c
	@echo 'static void test_cleanup() { printf("Test cleanup\\n"); }' >> plugin_test.c
	@echo 'plugin_info_t plugin_info = {' >> plugin_test.c
	@echo '  .name = "Test Plugin", .version = "1.0",' >> plugin_test.c
	@echo '  .initialize = test_init, .execute = test_exec, .cleanup = test_cleanup' >> plugin_test.c
	@echo '};' >> plugin_test.c
	@$(CC) $(PLUGIN_CFLAGS) $(PLUGIN_LDFLAGS) -o $(PLUGIN_DIR)/plugin_test.so plugin_test.c
	@echo "$(GREEN)✓$(NC) Test plugin created"
	@echo ""
	@echo "$(YELLOW)Testing with new plugin:$(NC)"
	@./plugin_loader
	@rm -f plugin_test.c $(PLUGIN_DIR)/plugin_test.so
	@echo ""
	@echo "$(GREEN)✓$(NC) Plugin development test complete"

# Clean build artifacts
clean:
	@echo "$(YELLOW)Cleaning dlopen-demo...$(NC)"
	@rm -f $(PROGRAMS) *.o $(PARENT_LIB)
	@rm -rf $(PLUGIN_DIR)
	@rm -f plugin_test.c
	@echo "$(GREEN)✓$(NC) Clean complete"

# Help target
help:
	@echo "dlopen/Plugin Makefile Targets:"
	@echo "  make all          - Build all programs and plugins"
	@echo "  make plugins      - Build plugins only"
	@echo "  make test         - Run tests"
	@echo "  make analysis     - Plugin system analysis"
	@echo "  make advanced-test - Advanced dlopen features"
	@echo "  make plugin-dev   - Test plugin development"
	@echo "  make clean        - Remove build artifacts"