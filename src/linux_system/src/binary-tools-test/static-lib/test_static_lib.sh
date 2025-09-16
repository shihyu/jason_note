#!/bin/bash

echo "=== Testing Static Library Creation and Usage ==="
echo

# 編譯目標文件
echo "1. Compiling object files..."
gcc -c math_utils.c -o math_utils.o
gcc -c string_utils.c -o string_utils.o

# 創建靜態庫
echo -e "\n2. Creating static library..."
ar rcs libutils.a math_utils.o string_utils.o

# 查看靜態庫內容
echo -e "\n3. Viewing static library contents:"
ar -t libutils.a

echo -e "\n4. Detailed library contents:"
ar -tv libutils.a

# 查看庫中的符號
echo -e "\n5. Symbols in static library:"
nm libutils.a

# 編譯使用靜態庫的程序 - 方法1
echo -e "\n6. Compiling with static library (Method 1 - direct):"
gcc main_static.c libutils.a -lm -o program_static1

# 編譯使用靜態庫的程序 - 方法2
echo -e "\n7. Compiling with static library (Method 2 - using -L and -l):"
gcc main_static.c -L. -lutils -lm -o program_static2

# 驗證靜態鏈接
echo -e "\n8. Verifying static linking:"
echo "ldd output (should not show libutils.a):"
ldd program_static1 | head -5

echo -e "\n9. Checking embedded symbols:"
nm program_static1 | grep calculate_area

echo -e "\n10. Running the static program:"
./program_static1

# 比較程序大小
echo -e "\n11. Comparing program sizes:"
ls -lh program_static*

# 提取單個目標文件
echo -e "\n12. Extracting single object from archive:"
ar -x libutils.a math_utils.o
file math_utils.o