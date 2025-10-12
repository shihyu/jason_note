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