#!/bin/bash

echo "=== Testing Dynamic Linking Tools and LD Variables ==="
echo

cd dynamic-lib

# 1. ldd tests
echo "1. Testing ldd:"
echo "Basic ldd output:"
ldd program_dynamic_rpath

echo -e "\nUnused dependencies check (-u):"
ldd -u program_dynamic_rpath

echo -e "\nVerbose output (-v):"
ldd -v program_dynamic_rpath | head -20

# 2. LD_LIBRARY_PATH test
echo -e "\n2. Testing LD_LIBRARY_PATH:"
LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH ldd program_dynamic | grep libdynamic

# 3. LD_DEBUG tests
echo -e "\n3. Testing LD_DEBUG:"

echo -e "\nLD_DEBUG=help (showing available options):"
LD_DEBUG=help ./program_dynamic_rpath 2>&1 | head -20

echo -e "\nLD_DEBUG=libs (library search):"
LD_LIBRARY_PATH=. LD_DEBUG=libs ./program_dynamic 2>&1 | grep "searching\|found" | head -5

echo -e "\nLD_DEBUG=symbols (symbol resolution):"
LD_LIBRARY_PATH=. LD_DEBUG=symbols ./program_dynamic 2>&1 | grep "symbol=" | head -3

echo -e "\nLD_DEBUG=bindings (symbol binding):"
LD_LIBRARY_PATH=. LD_DEBUG=bindings ./program_dynamic 2>&1 | grep "binding" | head -3

echo -e "\nLD_DEBUG=statistics:"
LD_LIBRARY_PATH=. LD_DEBUG=statistics ./program_dynamic 2>&1 | tail -10

# 4. LD_PRELOAD test
echo -e "\n4. Testing LD_PRELOAD:"
cat > malloc_hook.c << 'EOF'
#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>
#include <stdlib.h>

static int malloc_count = 0;

void* malloc(size_t size) {
    static void* (*real_malloc)(size_t) = NULL;
    if (!real_malloc)
        real_malloc = dlsym(RTLD_NEXT, "malloc");

    void* ptr = real_malloc(size);
    malloc_count++;
    if (malloc_count <= 5) {  // Only print first 5 calls
        fprintf(stderr, "[HOOK] malloc(%zu) = %p (call #%d)\n", size, ptr, malloc_count);
    }
    return ptr;
}
EOF

gcc -shared -fPIC -o malloc_hook.so malloc_hook.c -ldl
echo "Running with malloc hook:"
LD_PRELOAD=./malloc_hook.so ls /tmp > /dev/null 2>&1
LD_PRELOAD=./malloc_hook.so echo "Testing malloc hook" 2>&1 | head -5

# 5. LD_BIND_NOW test
echo -e "\n5. Testing LD_BIND_NOW:"
echo "Without LD_BIND_NOW (lazy binding):"
time LD_LIBRARY_PATH=. ./program_dynamic > /dev/null 2>&1
echo "With LD_BIND_NOW (immediate binding):"
time LD_BIND_NOW=1 LD_LIBRARY_PATH=. ./program_dynamic > /dev/null 2>&1

# 6. ldconfig cache inspection
echo -e "\n6. Testing ldconfig:"
echo "System library cache (first 10 entries):"
ldconfig -p | head -10

echo -e "\nSearching for specific library in cache:"
ldconfig -p | grep libm.so

# 7. Check RPATH/RUNPATH
echo -e "\n7. Checking RPATH/RUNPATH:"
readelf -d program_dynamic_rpath | grep -E "RPATH|RUNPATH"

# 8. LD_SHOW_AUXV test
echo -e "\n8. Testing LD_SHOW_AUXV (auxiliary vector):"
LD_SHOW_AUXV=1 /bin/true 2>&1 | head -10

# 9. Safe alternatives to ldd
echo -e "\n9. Safe alternatives to ldd:"
echo "Using objdump:"
objdump -p program_dynamic | grep NEEDED

echo -e "\nUsing readelf:"
readelf -d program_dynamic | grep NEEDED