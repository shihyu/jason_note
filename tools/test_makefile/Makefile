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
