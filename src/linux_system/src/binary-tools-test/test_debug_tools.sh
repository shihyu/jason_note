#!/bin/bash

echo "=== Testing Debugging and Tracing Tools ==="
echo

cd core-tools

# 1. strace tests
echo "1. Testing strace:"

echo -e "\nBasic strace (first 10 system calls):"
strace -e trace=file ./simple_test 2>&1 | head -10

echo -e "\nStrace with timestamps (-t):"
strace -t -e open,openat,close ls /tmp 2>&1 | head -5

echo -e "\nStrace statistics (-c):"
strace -c ls /tmp > /dev/null 2>&1

echo -e "\nStrace specific calls (memory operations):"
strace -e trace=memory echo "test" 2>&1 | head -5

# 2. ltrace tests (if available)
echo -e "\n2. Testing ltrace:"
if command -v ltrace &> /dev/null; then
    echo "Basic ltrace (first 10 library calls):"
    ltrace ./simple_test 2>&1 | head -10

    echo -e "\nLtrace with counts (-c):"
    ltrace -c ls /tmp > /dev/null 2>&1
else
    echo "ltrace not installed, skipping..."
fi

# 3. Create test for performance analysis
echo -e "\n3. Creating performance test program..."
cat > perf_test.c << 'EOF'
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

double compute_intensive(int n) {
    double sum = 0;
    for (int i = 0; i < n; i++) {
        sum += sqrt(i) * sin(i);
    }
    return sum;
}

int main() {
    printf("Starting performance test...\n");
    for (int i = 0; i < 5; i++) {
        double result = compute_intensive(1000000);
        printf("Iteration %d: %f\n", i, result);
    }
    return 0;
}
EOF

gcc -o perf_test perf_test.c -lm -g

# 4. gprof test (if compiled with -pg)
echo -e "\n4. Testing gprof:"
gcc -pg -o perf_test_gprof perf_test.c -lm
./perf_test_gprof > /dev/null
if [ -f gmon.out ]; then
    echo "Generating gprof report:"
    gprof perf_test_gprof gmon.out | head -20
else
    echo "gmon.out not generated"
fi

# 5. valgrind test (if available)
echo -e "\n5. Testing valgrind (memory check):"
if command -v valgrind &> /dev/null; then
    cat > mem_test.c << 'EOF'
#include <stdlib.h>
#include <string.h>

int main() {
    char *buffer = malloc(100);
    strcpy(buffer, "Hello");
    // Intentional memory leak - not freeing buffer
    return 0;
}
EOF
    gcc -g -o mem_test mem_test.c
    valgrind --leak-check=yes --log-file=valgrind.log ./mem_test 2>/dev/null
    echo "Valgrind output:"
    cat valgrind.log | grep -E "definitely lost|ERROR SUMMARY" | head -5
else
    echo "valgrind not installed, skipping..."
fi

# 6. perf test (if available)
echo -e "\n6. Testing perf:"
if command -v perf &> /dev/null; then
    echo "Basic perf stat:"
    perf stat -e cycles,instructions ./perf_test 2>&1 | grep -E "cycles|instructions|seconds"
else
    echo "perf not installed, skipping..."
fi

# 7. checksec test
echo -e "\n7. Testing security features:"
echo "Checking binary security features:"

# Manual security checks if checksec not available
echo -e "\nManual security checks for simple_test:"
echo -n "RELRO: "
readelf -l simple_test | grep -q GNU_RELRO && echo "Yes" || echo "No"

echo -n "Stack Canary: "
nm simple_test | grep -q __stack_chk && echo "Yes" || echo "No"

echo -n "NX: "
readelf -l simple_test | grep GNU_STACK | grep -q "RW" && echo "Yes (NX enabled)" || echo "No"

echo -n "PIE: "
readelf -h simple_test | grep -q "DYN" && echo "Yes" || echo "No"

echo -n "FORTIFY: "
nm simple_test | grep -q _chk && echo "Possible" || echo "No"

# 8. Test LD_DEBUG with our programs
echo -e "\n8. Advanced LD_DEBUG with our test programs:"
cd ../dynamic-lib
LD_LIBRARY_PATH=. LD_DEBUG=statistics ./program_dynamic 2>&1 | grep -E "relocations|cycles"