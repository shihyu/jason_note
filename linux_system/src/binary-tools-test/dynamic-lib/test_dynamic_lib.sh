#!/bin/bash

echo "=== Testing Dynamic Library Creation and Usage ==="
echo

# 1. 基本動態庫編譯
echo "1. Creating basic dynamic library..."
gcc -fPIC -c dynamic_lib.c -o dynamic_lib.o
gcc -shared -o libdynamic.so dynamic_lib.o

# 2. 帶 SONAME 的動態庫
echo -e "\n2. Creating dynamic library with SONAME..."
gcc -fPIC -shared -Wl,-soname,libdynamic.so.1 -o libdynamic.so.1.0 dynamic_lib.c
ln -sf libdynamic.so.1.0 libdynamic.so.1
ln -sf libdynamic.so.1 libdynamic.so

# 3. 控制符號可見性
echo -e "\n3. Creating library with controlled visibility..."
gcc -fPIC -fvisibility=hidden -shared -o libdynamic_hidden.so dynamic_lib.c

# 4. 查看導出符號
echo -e "\n4. Exported symbols (normal vs hidden):"
echo "Normal library:"
nm -D libdynamic.so | grep -E "T|D"

echo -e "\nHidden visibility library:"
nm -D libdynamic_hidden.so | grep -E "T|D"

# 5. 查看動態庫信息
echo -e "\n5. Dynamic library information:"
readelf -d libdynamic.so.1.0 | grep SONAME

# 6. 編譯使用動態庫的程序
echo -e "\n6. Compiling program with dynamic library..."
gcc main_dynamic.c -L. -ldynamic -o program_dynamic

# 7. 查看依賴
echo -e "\n7. Checking dependencies:"
ldd program_dynamic

# 8. 設置 LD_LIBRARY_PATH 並運行
echo -e "\n8. Running with LD_LIBRARY_PATH:"
LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH ./program_dynamic

# 9. 使用 rpath 編譯
echo -e "\n9. Compiling with RPATH:"
gcc main_dynamic.c -L. -ldynamic -Wl,-rpath,. -o program_dynamic_rpath
echo "Dependencies with RPATH:"
readelf -d program_dynamic_rpath | grep -E "RPATH|RUNPATH"

echo -e "\n10. Running program with RPATH (no LD_LIBRARY_PATH needed):"
./program_dynamic_rpath

# 11. LD_DEBUG 測試
echo -e "\n11. Testing LD_DEBUG:"
echo "Library search paths:"
LD_LIBRARY_PATH=. LD_DEBUG=libs ./program_dynamic 2>&1 | grep "searching" | head -3

# 12. 比較文件大小
echo -e "\n12. Comparing sizes:"
ls -lh libdynamic*.so* program_dynamic*