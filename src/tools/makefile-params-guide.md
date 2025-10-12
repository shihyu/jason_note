# Makefile 編譯參數說明

## Makefile 內容
```makefile
CC = gcc
CFLAGS = -g -Wall
INCLUDE = -I../include -I../ggml/include
LDFLAGS = -L../build/bin -lllama -lggml -lggml-base -lggml-cpu
RPATH = -Wl,-rpath,../build/bin
```

---

## 各變數詳細說明

### CC = gcc
- **用途**: 指定編譯器為 gcc（GNU C Compiler）
- **好處**: 
  - 統一編譯器版本，確保團隊使用相同工具
  - 方便切換編譯器（改成 `clang` 就能換編譯器）

### CFLAGS = -g -Wall
- **用途**: 編譯選項標誌
- **參數說明**:
  - `-g`: 生成除錯資訊，讓你可以用 gdb 等工具除錯
  - `-Wall`: 開啟所有常見的編譯警告，幫助發現潛在問題

### INCLUDE = -I../include -I../ggml/include
- **用途**: 指定標頭檔 (.h) 的搜尋路徑
- **參數說明**:
  - `-I../include`: 在上層目錄的 include 中尋找標頭檔
  - `-I../ggml/include`: 在 ggml 函式庫的 include 目錄中尋找標頭檔
- **作用**: 讓編譯器能找到 `#include <xxx.h>` 所需的檔案

### LDFLAGS = -L../build/bin -lllama -lggml -lggml-base -lggml-cpu
- **用途**: 連結器選項
- **參數說明**:
  - `-L../build/bin`: 指定函式庫檔案 (.so/.a) 的搜尋路徑
  - `-lllama`: 連結 llama 函式庫 (libllama.so)
  - `-lggml`、`-lggml-base`、`-lggml-cpu`: 連結 ggml 相關函式庫
- **作用**: 這些是執行程式所需的外部函式庫

### RPATH = -Wl,-rpath,../build/bin
- **用途**: 設定執行期函式庫搜尋路徑
- **參數說明**:
  - `-Wl`: 將後面的參數傳給連結器
  - `-rpath,../build/bin`: 在執行檔中嵌入函式庫搜尋路徑
- **重要**: 讓程式執行時能找到 .so 檔，不用設定 `LD_LIBRARY_PATH` 環境變數

---

## 編譯階段 vs 連結階段

### 編譯階段（Compilation）
將 `.c` 原始碼轉換成 `.o` 目標檔

**使用的參數**:
```makefile
CC = gcc                                    # 編譯器
CFLAGS = -g -Wall                          # 編譯選項
INCLUDE = -I../include -I../ggml/include   # 標頭檔搜尋路徑
```

- `-g`, `-Wall`: 控制如何編譯程式碼
- `-I`: 告訴編譯器去哪裡找 `#include` 的標頭檔

### 連結階段（Linking）
將 `.o` 目標檔和函式庫連結成可執行檔

**使用的參數**:
```makefile
LDFLAGS = -L../build/bin -lllama -lggml -lggml-base -lggml-cpu  # 連結選項
RPATH = -Wl,-rpath,../build/bin                                  # 執行期路徑
```

- `-L`: 指定函式庫檔案的搜尋路徑
- `-l`: 指定要連結哪些函式庫
- `-Wl,-rpath`: 設定執行時期的函式庫搜尋路徑（給 linker 的指令）

---

## 編譯命令對比

### 目前的 Makefile（一步完成）
```bash
gcc -g -Wall -o test_4_so test_4_so.c -I../include -I../ggml/include \
    -L../build/bin -lllama -lggml -lggml-base -lggml-cpu \
    -Wl,-rpath,../build/bin
```

### 分成兩步的方式

**步驟 1: 編譯（只用編譯階段參數）**
```bash
gcc -g -Wall -I../include -I../ggml/include -c test_4_so.c -o test_4_so.o
```

**步驟 2: 連結（只用連結階段參數）**
```bash
gcc -o test_4_so test_4_so.o -L../build/bin \
    -lllama -lggml -lggml-base -lggml-cpu \
    -Wl,-rpath,../build/bin
```

---

## 使用變數的好處

1. **可維護性**: 集中管理編譯選項，修改更容易
2. **可讀性**: 清楚分類各種參數，一目了然
3. **可重用性**: 多個目標可以共用相同設定
4. **避免錯誤**: 不用每次都輸入一長串命令

---

## 注意事項

- 一步完成編譯比較方便，適合小型專案
- 大型專案通常會分開編譯和連結，以節省重新編譯時間
- RPATH 的設定讓程式可以找到動態函式庫，避免執行時找不到 .so 檔的問題

---

## 查看連結資訊的工具

### 1. ldd - 最簡單直觀
查看程式執行時會載入哪些動態函式庫：

```bash
ldd test_4_so
```

輸出範例：
```
libllama.so => ../build/bin/libllama.so (0x00007f...)
libggml.so => ../build/bin/libggml.so (0x00007f...)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f...)
```

### 2. readelf -d - 查看動態段（最詳細）
```bash
readelf -d test_4_so
```

可以看到：
- **NEEDED**: 連結了哪些函式庫（`-l` 參數的結果）
- **RPATH/RUNPATH**: 執行期搜尋路徑（`-Wl,-rpath` 的結果）
- **SONAME**: 函式庫的名稱

輸出範例：
```
Dynamic section at offset 0x2d40 contains 28 entries:
  Tag        Type           Name/Value
 0x0000001d (RUNPATH)       Library runpath: [../build/bin]
 0x00000001 (NEEDED)        Shared library: [libllama.so]
 0x00000001 (NEEDED)        Shared library: [libggml.so]
 0x00000001 (NEEDED)        Shared library: [libc.so.6]
```

### 3. objdump -p - 查看程式標頭
```bash
objdump -p test_4_so | grep -E "NEEDED|RPATH|RUNPATH"
```

類似 readelf，但輸出格式不同

### 4. nm - 查看符號表
```bash
nm -D test_4_so    # 查看動態符號
nm test_4_so       # 查看所有符號
```

用途：查看函式庫中定義了哪些函數/變數，但**不顯示 rpath 或 NEEDED**

---

## 工具對照表

| 資訊 | 最佳工具 | 指令 |
|------|---------|------|
| **連結了哪些函式庫** (`-l`) | `ldd` 或 `readelf -d` | `ldd test_4_so` |
| **RPATH 路徑** (`-Wl,-rpath`) | `readelf -d` | `readelf -d test_4_so \| grep RPATH` |
| **函式庫搜尋路徑** (`-L`) | ❌ 無法查看 | 編譯期資訊，不會存在執行檔中 |
| **符號/函數名稱** | `nm` | `nm -D libllama.so` |

---

## 實用指令範例

```bash
# 快速查看所有動態連結資訊
readelf -d test_4_so

# 只看 RPATH/RUNPATH
readelf -d test_4_so | grep -E "RPATH|RUNPATH"

# 只看連結的函式庫
readelf -d test_4_so | grep NEEDED

# 查看實際載入路徑
ldd test_4_so

# 查看 libllama.so 提供了哪些符號
nm -D ../build/bin/libllama.so | grep " T "  # T = 已定義的函數

# 查看未定義的符號（需要從其他函式庫載入）
nm -D test_4_so | grep " U "  # U = 未定義的符號
```

**重要提醒**: `-L` 的路徑只在編譯時使用，不會記錄在執行檔中。只有 RPATH/RUNPATH 會被寫入執行檔！

---

## 完整測試範例

以下是一個完整的測試專案，幫助你驗證所有編譯參數和工具的使用。

### 建立測試專案腳本

將以下內容儲存為 `setup_test.sh`：

```bash
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
echo "測試完成！"
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
```

### 使用方式

```bash
# 1. 儲存並執行建立腳本
chmod +x setup_test.sh
./setup_test.sh

# 2. 進入測試目錄
cd test_makefile

# 3. 執行完整測試
./test_all.sh
```

### 測試專案包含內容

- **自製動態函式庫** (`libmylib.so`)：包含兩個簡單函數
- **主程式** (`main`)：使用該函式庫
- **完整 Makefile**：展示所有編譯參數的使用
- **測試腳本**：自動執行並檢查所有工具輸出

### 預期輸出

執行 `./test_all.sh` 後你會看到：

1. **編譯過程**：展示 `-I`、`-L`、`-l`、`-Wl,-rpath` 的實際使用
2. **程式執行**：驗證函式庫正確連結
   ```
   === Testing Library Functions ===
   Hello User from mylib!
   10 + 20 = 30
   ```
3. **ldd 輸出**：顯示載入的動態函式庫路徑
4. **readelf 輸出**：顯示 RPATH 和 NEEDED 資訊
5. **nm 輸出**：顯示符號表中的函數
6. **objdump 輸出**：另一種查看方式

### 實驗建議

```bash
# 實驗 1: 移除 RPATH 看看會發生什麼
# 在 Makefile 中註解掉 RPATH 這行，重新編譯
# 執行時會找不到 libmylib.so

# 實驗 2: 比較不同工具的輸出
ldd build/main                    # 最直觀
readelf -d build/main             # 最詳細
objdump -p build/main             # 另一種格式
nm -D build/libmylib.so           # 查看符號

# 實驗 3: 查看特定資訊
readelf -d build/main | grep RPATH      # 只看 RPATH
readelf -d build/main | grep NEEDED     # 只看依賴
nm -D build/libmylib.so | grep " T "    # 只看已定義函數
```

### 專案結構說明

```
test_makefile/
├── include/
│   └── mylib.h           # 標頭檔 (對應 -I 參數)
├── lib/
│   └── mylib.c           # 函式庫原始碼
├── src/
│   └── main.c            # 主程式原始碼
├── build/                # 輸出目錄 (對應 -L 和 -rpath)
│   ├── libmylib.so       # 編譯出的動態函式庫
│   └── main              # 編譯出的執行檔
├── Makefile              # 建構腳本
└── test_all.sh           # 測試腳本
```