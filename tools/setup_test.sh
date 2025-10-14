#!/bin/bash
# 建立測試專案結構

echo "=== 建立測試專案 ==="
mkdir -p test_makefile/{lib,include,src,build}
cd test_makefile

# 1. 建立標頭檔
cat > include/mylib.h << 'EOF'
#ifndef MYLIB_H
#define MYLIB_H

void hello_from_lib(const char* name);
int add_numbers(int a, int b);

#endif
EOF

# 2. 建立函式庫原始碼
cat > lib/mylib.c << 'EOF'
#include <stdio.h>
#include "mylib.h"

void hello_from_lib(const char* name) {
    printf("Hello %s from mylib!\n", name);
}

int add_numbers(int a, int b) {
    return a + b;
}
EOF

# 3. 建立主程式
cat > src/main.c << 'EOF'
#include <stdio.h>
#include "mylib.h"

int main() {
    printf("=== Testing Library Functions ===\n");
    hello_from_lib("User");

    int result = add_numbers(10, 20);
    printf("10 + 20 = %d\n", result);

    return 0;
}
EOF

# 4. 建立 Makefile
cat > Makefile << 'EOF'
CC = gcc
CFLAGS = -g -Wall -fPIC
INCLUDE = -Iinclude
LDFLAGS = -Lbuild -lmylib
RPATH = -Wl,-rpath,./build

all: build/libmylib.so build/main

# 編譯動態函式庫
build/libmylib.so: lib/mylib.c
	@echo "=== 編譯動態函式庫 ==="
	$(CC) $(CFLAGS) -shared -o $@ $< $(INCLUDE)

# 編譯主程式
build/main: src/main.c build/libmylib.so
	@echo "=== 編譯主程式 ==="
	$(CC) $(CFLAGS) -o $@ $< $(INCLUDE) $(LDFLAGS) $(RPATH)

clean:
	rm -rf build/*

test: all
	@echo ""
	@echo "=== 執行程式 ==="
	./build/main

inspect: all
	@echo ""
	@echo "=========================================="
	@echo "1. 使用 ldd 查看依賴的函式庫"
	@echo "=========================================="
	ldd build/main
	@echo ""
	@echo "=========================================="
	@echo "2. 使用 readelf 查看 NEEDED 和 RPATH"
	@echo "=========================================="
	readelf -d build/main | grep -E "NEEDED|RPATH|RUNPATH"
	@echo ""
	@echo "=========================================="
	@echo "3. 使用 nm 查看函式庫的符號"
	@echo "=========================================="
	@echo "已定義的函數 (T):"
	nm -D build/libmylib.so | grep " T "
	@echo ""
	@echo "=========================================="
	@echo "4. 使用 nm 查看主程式未定義的符號 (需要從函式庫載入)"
	@echo "=========================================="
	nm -D build/main | grep " U " | grep -E "hello|add"
	@echo ""
	@echo "=========================================="
	@echo "5. 使用 objdump 查看動態段"
	@echo "=========================================="
	objdump -p build/main | grep -E "NEEDED|RPATH|RUNPATH"

.PHONY: all clean test inspect
EOF

# 5. 建立測試腳本
cat > test_all.sh << 'EOF'
#!/bin/bash

echo "======================================"
echo "開始完整測試流程"
echo "======================================"

# 清理並編譯
echo ""
echo ">>> Step 1: 清理舊檔案"
make clean

echo ""
echo ">>> Step 2: 編譯專案"
make all

echo ""
echo ">>> Step 3: 執行程式測試"
make test

echo ""
echo ">>> Step 4: 檢查連結資訊"
make inspect

echo ""
echo "======================================"
echo "測試完成!"
echo "======================================"
EOF

chmod +x test_all.sh

echo ""
echo "✅ 測試專案建立完成！"
echo ""
echo "📁 專案結構："
echo "test_makefile/"
echo "├── include/mylib.h      (標頭檔)"
echo "├── lib/mylib.c          (函式庫原始碼)"
echo "├── src/main.c           (主程式)"
echo "├── build/               (輸出目錄)"
echo "├── Makefile             (建構檔)"
echo "└── test_all.sh          (測試腳本)"
echo ""
echo "🚀 執行測試："
echo "   cd test_makefile"
echo "   ./test_all.sh"
echo ""
echo "或分步執行："
echo "   make all       # 編譯"
echo "   make test      # 執行"
echo "   make inspect   # 檢查連結資訊"
echo "   make clean     # 清理"
