# Makefile for Dynamic Library Tests

CC = gcc
CFLAGS = -Wall -g -fPIC
LDFLAGS = -shared
SONAME = libdynamic.so.1
REALNAME = libdynamic.so.1.0

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# Library files
LIBS = libdynamic.so $(SONAME) $(REALNAME) libdynamic_hidden.so

# Test programs
PROGRAMS = program_dynamic program_dynamic_rpath

# LD_PRELOAD hook
HOOK_LIB = malloc_hook.so

.PHONY: all clean test lib analysis ld-test

all: lib $(PROGRAMS) $(HOOK_LIB)
	@echo "$(GREEN)✓$(NC) Dynamic libraries and programs built"

# Build dynamic libraries
lib: $(LIBS)

# Basic dynamic library
libdynamic.so: dynamic_lib.o
	@echo "$(YELLOW)Creating basic dynamic library$(NC) $@..."
	@$(CC) $(LDFLAGS) -o $@ $^

# Dynamic library with SONAME
$(REALNAME): dynamic_lib.c
	@echo "$(YELLOW)Creating versioned dynamic library$(NC) $@..."
	@$(CC) $(CFLAGS) $(LDFLAGS) -Wl,-soname,$(SONAME) -o $@ $<

$(SONAME): $(REALNAME)
	@echo "$(YELLOW)Creating symlink$(NC) $@..."
	@ln -sf $< $@

libdynamic.so: $(SONAME)
	@echo "$(YELLOW)Creating symlink$(NC) $@..."
	@ln -sf $< $@

# Library with hidden visibility
libdynamic_hidden.so: dynamic_lib.c
	@echo "$(YELLOW)Creating library with hidden visibility$(NC) $@..."
	@$(CC) $(CFLAGS) -fvisibility=hidden $(LDFLAGS) -o $@ $<

# Object files
dynamic_lib.o: dynamic_lib.c
	@echo "$(YELLOW)Compiling$(NC) $<..."
	@$(CC) $(CFLAGS) -c $< -o $@

# Test programs
program_dynamic: main_dynamic.c $(SONAME)
	@echo "$(YELLOW)Building$(NC) $@ (using LD_LIBRARY_PATH)..."
	@$(CC) $(CFLAGS:-fPIC=) $< -L. -ldynamic -o $@

program_dynamic_rpath: main_dynamic.c $(SONAME)
	@echo "$(YELLOW)Building$(NC) $@ (with RPATH)..."
	@$(CC) $(CFLAGS:-fPIC=) $< -L. -ldynamic -Wl,-rpath,. -o $@

# LD_PRELOAD hook library
$(HOOK_LIB): malloc_hook.c
	@echo "$(YELLOW)Building$(NC) malloc hook library..."
	@$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $< -ldl

malloc_hook.c:
	@echo "Creating malloc_hook.c..."
	@echo '#define _GNU_SOURCE' > $@
	@echo '#include <stdio.h>' >> $@
	@echo '#include <dlfcn.h>' >> $@
	@echo '#include <stdlib.h>' >> $@
	@echo '' >> $@
	@echo 'static int malloc_count = 0;' >> $@
	@echo '' >> $@
	@echo 'void* malloc(size_t size) {' >> $@
	@echo '    static void* (*real_malloc)(size_t) = NULL;' >> $@
	@echo '    if (!real_malloc)' >> $@
	@echo '        real_malloc = dlsym(RTLD_NEXT, "malloc");' >> $@
	@echo '    void* ptr = real_malloc(size);' >> $@
	@echo '    malloc_count++;' >> $@
	@echo '    if (malloc_count <= 3) {' >> $@
	@echo '        fprintf(stderr, "[HOOK] malloc(%zu) = %p\\n", size, ptr);' >> $@
	@echo '    }' >> $@
	@echo '    return ptr;' >> $@
	@echo '}' >> $@

# Run tests
test: all
	@echo "$(YELLOW)=== Testing Dynamic Library ===$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Library information:$(NC)"
	@readelf -d $(REALNAME) | grep SONAME
	@echo ""
	@echo "$(YELLOW)2. Exported symbols (normal vs hidden):$(NC)"
	@echo "  Normal library:"
	@nm -D libdynamic.so | grep -E " T " | head -5
	@echo "  Hidden visibility:"
	@nm -D libdynamic_hidden.so | grep -E " T " | head -5
	@echo ""
	@echo "$(YELLOW)3. Running with LD_LIBRARY_PATH:$(NC)"
	@LD_LIBRARY_PATH=.:$$LD_LIBRARY_PATH ./program_dynamic
	@echo ""
	@echo "$(YELLOW)4. Running with RPATH:$(NC)"
	@./program_dynamic_rpath
	@echo ""
	@echo "$(YELLOW)5. Checking dependencies:$(NC)"
	@ldd program_dynamic_rpath | head -5
	@echo ""
	@echo "$(YELLOW)6. Testing LD_PRELOAD hook:$(NC)"
	@LD_PRELOAD=./$(HOOK_LIB) echo "Testing malloc hook" 2>&1 | head -5
	@echo ""
	@echo "$(GREEN)✓$(NC) Dynamic library tests completed"

# Library analysis
analysis: lib
	@echo "$(YELLOW)=== Dynamic Library Analysis ===$(NC)"
	@echo ""
	@echo "$(YELLOW)File information:$(NC)"
	@file $(REALNAME)
	@echo ""
	@echo "$(YELLOW)ELF header:$(NC)"
	@readelf -h $(REALNAME) | head -15
	@echo ""
	@echo "$(YELLOW)Dynamic section:$(NC)"
	@readelf -d $(REALNAME)
	@echo ""
	@echo "$(YELLOW)Symbol versions:$(NC)"
	@readelf -V $(REALNAME) | head -20 || echo "  No version information"
	@echo ""
	@echo "$(YELLOW)All exported symbols:$(NC)"
	@nm -D $(REALNAME)
	@echo ""
	@echo "$(GREEN)✓$(NC) Analysis complete"

# LD environment tests
ld-test: all
	@echo "$(YELLOW)=== Testing LD Environment Variables ===$(NC)"
	@echo ""
	@echo "$(YELLOW)1. LD_DEBUG=help:$(NC)"
	@LD_DEBUG=help ./program_dynamic_rpath 2>&1 | head -10
	@echo ""
	@echo "$(YELLOW)2. LD_DEBUG=libs:$(NC)"
	@LD_LIBRARY_PATH=. LD_DEBUG=libs ./program_dynamic 2>&1 | grep "searching\|found" | head -5
	@echo ""
	@echo "$(YELLOW)3. LD_DEBUG=statistics:$(NC)"
	@LD_LIBRARY_PATH=. LD_DEBUG=statistics ./program_dynamic 2>&1 | tail -10
	@echo ""
	@echo "$(YELLOW)4. LD_BIND_NOW test:$(NC)"
	@time LD_LIBRARY_PATH=. ./program_dynamic > /dev/null 2>&1
	@time LD_BIND_NOW=1 LD_LIBRARY_PATH=. ./program_dynamic > /dev/null 2>&1
	@echo ""
	@echo "$(GREEN)✓$(NC) LD tests completed"

# RPATH/RUNPATH comparison
rpath-test: program_dynamic_rpath
	@echo "$(YELLOW)=== RPATH/RUNPATH Analysis ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Checking RPATH/RUNPATH:$(NC)"
	@readelf -d program_dynamic_rpath | grep -E "RPATH|RUNPATH"
	@echo ""
	@echo "$(YELLOW)Library search order test:$(NC)"
	@LD_DEBUG=libs ./program_dynamic_rpath 2>&1 | grep "search\|found" | head -10
	@echo ""
	@echo "$(GREEN)✓$(NC) RPATH test complete"

# Clean build artifacts
clean:
	@echo "$(YELLOW)Cleaning dynamic-lib...$(NC)"
	@rm -f *.o *.so *.so.* $(PROGRAMS) malloc_hook.c
	@echo "$(GREEN)✓$(NC) Clean complete"

# Help target
help:
	@echo "Dynamic Library Makefile Targets:"
	@echo "  make all       - Build libraries and test programs"
	@echo "  make lib       - Build dynamic libraries only"
	@echo "  make test      - Run tests"
	@echo "  make analysis  - Detailed library analysis"
	@echo "  make ld-test   - Test LD environment variables"
	@echo "  make rpath-test - Test RPATH/RUNPATH"
	@echo "  make clean     - Remove build artifacts"