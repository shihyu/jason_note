#!/bin/bash

echo "=== Testing Core Binary Analysis Tools ==="
echo

# 1. nm tests
echo "=== 1. Testing nm ==="
echo "Basic nm output:"
nm simple_test | head -10

echo -e "\nShow external symbols only (-g):"
nm -g simple_test | head -5

echo -e "\nShow undefined symbols only (-u):"
nm -u simple_test | head -5

echo -e "\nSort by address (-n):"
nm -n simple_test | head -5

echo -e "\nDemangle C++ symbols (-C) - testing on system binary:"
nm -C /usr/bin/c++ 2>/dev/null | grep "std::" | head -3

# 2. objdump tests
echo -e "\n=== 2. Testing objdump ==="
echo "Disassemble main function:"
objdump -d simple_test | sed -n '/<main>:/,/^$/p' | head -20

echo -e "\nSection headers:"
objdump -h simple_test | head -20

echo -e "\nSymbol table:"
objdump -t simple_test | grep -E "(global_|public_|weak_)" | head -5

# 3. readelf tests
echo -e "\n=== 3. Testing readelf ==="
echo "ELF header:"
readelf -h simple_test | head -15

echo -e "\nProgram headers:"
readelf -l simple_test | head -20

echo -e "\nSection headers:"
readelf -S simple_test | head -15

echo -e "\nDynamic section:"
readelf -d simple_test | head -10

# 4. strings test
echo -e "\n=== 4. Testing strings ==="
echo "Extract strings from binary:"
strings simple_test | grep -E "(Hello|function|weak)"

echo -e "\nStrings with offsets:"
strings -t x simple_test | grep "Hello"

# 5. file test
echo -e "\n=== 5. Testing file ==="
file simple_test
file -b simple_test
file -i simple_test

# 6. size test
echo -e "\n=== 6. Testing size ==="
size simple_test
size -A simple_test | head -10