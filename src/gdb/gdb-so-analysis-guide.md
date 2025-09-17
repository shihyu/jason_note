# GDB 分析 .so/.a 檔案完整指南

## 基礎命令

### 1. 查看函數符號
```bash
# 列出所有函數
gdb lib.so -batch -ex "info functions"

# 過濾特定函數
gdb lib.so -batch -ex "info functions init"

# 使用正則表達式
gdb lib.so -batch -ex "info functions ^lib_.*_init$"

# 查看 C++ 函數（包含完整簽名）
gdb lib.so -batch -ex "info functions" -ex "set print asm-demangle on"
```

### 2. 查看變數符號
```bash
# 列出所有全域變數
gdb lib.so -batch -ex "info variables"

# 過濾特定變數
gdb lib.so -batch -ex "info variables config"

# 查看靜態變數
gdb lib.so -batch -ex "info variables ^static_"
```

### 3. 查看類型定義
```bash
# 列出所有類型
gdb lib.so -batch -ex "info types"

# 查看特定類型
gdb lib.so -batch -ex "info types MyClass"

# 查看 STL 類型
gdb lib.so -batch -ex "info types std::"
```

## 進階分析技巧

### 4. 反組譯函數
```bash
# 反組譯特定函數
gdb lib.so -batch -ex "disassemble function_name"

# 反組譯地址範圍
gdb lib.so -batch -ex "disassemble 0x1000,0x1100"

# Intel 語法（更易讀）
gdb lib.so -batch -ex "set disassembly-flavor intel" -ex "disassemble main"

# 顯示原始碼和組譯混合
gdb lib.so -batch -ex "disassemble /m function_name"
```

### 5. 查看段（Sections）資訊
```bash
# 列出所有段
gdb lib.so -batch -ex "maintenance info sections"

# 查看特定段
gdb lib.so -batch -ex "maintenance info sections .text"

# 查看段的記憶體映射
gdb lib.so -batch -ex "info files"
```

### 6. 查看依賴關係
```bash
# 查看動態連結的函式庫
gdb lib.so -batch -ex "info sharedlibrary"

# 查看 PLT (Procedure Linkage Table)
gdb lib.so -batch -ex "info functions @plt"

# 查看 GOT (Global Offset Table)
gdb lib.so -batch -ex "maintenance info sections .got"
```

## 符號分析

### 7. 符號表操作
```bash
# 查看所有符號
gdb lib.so -batch -ex "info all-symbols"

# 查看特定符號的詳細資訊
gdb lib.so -batch -ex "info symbol 0x12345678"

# 查看符號的地址
gdb lib.so -batch -ex "info address function_name"

# 列出原始檔
gdb lib.so -batch -ex "info sources"
```

### 8. C++ 特定功能
```bash
# 查看 C++ 類別
gdb lib.so -batch -ex "info classes"

# 查看虛擬函數表
gdb lib.so -batch -ex "info vtbl ClassName"

# 查看 namespace
gdb lib.so -batch -ex "info namespace"

# Demangle C++ 符號
gdb lib.so -batch -ex "set print demangle on" -ex "info functions"
```

## 記憶體和資料分析

### 9. 檢查資料結構
```bash
# 查看結構體定義
gdb lib.so -batch -ex "ptype struct MyStruct"

# 查看類別定義
gdb lib.so -batch -ex "ptype class MyClass"

# 查看枚舉
gdb lib.so -batch -ex "ptype enum MyEnum"

# 查看 typedef
gdb lib.so -batch -ex "info types typedef"
```

### 10. 導出符號資訊
```bash
# 產生符號檔案
gdb lib.so -batch -ex "maint print symbols symbols.txt"

# 產生部分符號表
gdb lib.so -batch -ex "maint print psymbols psymbols.txt"

# 產生最小符號表
gdb lib.so -batch -ex "maint print msymbols msymbols.txt"
```

## 實用組合技巧

### 11. 分析函數呼叫
```bash
# 找出所有呼叫 malloc 的地方
gdb lib.so -batch -ex "disassemble" | grep -B2 "call.*malloc"

# 列出所有 exported 函數（動態符號）
gdb lib.so -batch -ex "info functions" | grep -E "^[0-9a-fx]+ +[^<]"

# 統計函數數量
gdb lib.so -batch -ex "info functions" | grep -c "^0x"
```

### 12. 安全審計
```bash
# 尋找危險函數
gdb lib.so -batch -ex "info functions" | grep -E "(strcpy|gets|sprintf|system)"

# 檢查 RELRO (Relocation Read-Only)
gdb lib.so -batch -ex "info files" | grep -E "(GNU_RELRO|\.got)"

# 檢查 stack canary
gdb lib.so -batch -ex "info functions" | grep "__stack_chk"
```

## Shell 函數範例

### 基礎版本
```bash
# ~/.bashrc
soinfo() {
    local file="$1"
    local cmd="${2:-functions}"
    
    case "$cmd" in
        func|functions)
            gdb "$file" -batch -ex "info functions" ;;
        var|variables)
            gdb "$file" -batch -ex "info variables" ;;
        type|types)
            gdb "$file" -batch -ex "info types" ;;
        dis|disas)
            gdb "$file" -batch -ex "disassemble $3" ;;
        *)
            echo "Usage: soinfo <file> [func|var|type|dis] [args]"
            ;;
    esac
}
```

### 進階版本
```bash
# ~/.bashrc
soanalyze() {
    local file="$1"
    local analysis="$2"
    
    if [[ ! -f "$file" ]]; then
        echo "File not found: $file"
        return 1
    fi
    
    case "$analysis" in
        exports)
            echo "=== Exported Functions ==="
            gdb "$file" -batch -ex "info functions" | \
                grep -E "^0x[0-9a-f]+ +[A-Za-z_]"
            ;;
        cpp)
            echo "=== C++ Symbols ==="
            gdb "$file" -batch -ex "set print demangle on" \
                -ex "info functions" | grep -E "::|<|>"
            ;;
        security)
            echo "=== Security Check ==="
            echo "Dangerous functions:"
            gdb "$file" -batch -ex "info functions" | \
                grep -E "(strcpy|gets|sprintf|system)"
            echo -e "\nStack protection:"
            gdb "$file" -batch -ex "info functions" | \
                grep -c "__stack_chk" || echo "No stack canary found"
            ;;
        stats)
            echo "=== Library Statistics ==="
            echo "Functions: $(gdb "$file" -batch -ex "info functions" | grep -c "^0x")"
            echo "Variables: $(gdb "$file" -batch -ex "info variables" | grep -c "^0x")"
            echo "Types: $(gdb "$file" -batch -ex "info types" | grep -c "^File\|^type")"
            ;;
        *)
            echo "Usage: soanalyze <file> [exports|cpp|security|stats]"
            ;;
    esac
}
```

### 結合 nm 和 GDB 的智慧函數
```bash
# ~/.bashrc

# 快速符號查看（用 nm）
qsym() {
    nm -DC "$1" | grep -E " [TDG] " | less
}

# 詳細分析（用 GDB）
dsym() {
    gdb "$1" -batch -ex "info functions" -ex "info variables" | less
}

# 智慧選擇工具
sym() {
    local file="$1"
    local pattern="$2"
    
    if [[ -z "$pattern" ]]; then
        # 沒有 pattern，用 nm（快）
        nm -DC "$file"
    else
        # 有 pattern，用 GDB（功能強）
        gdb "$file" -batch -ex "info functions $pattern"
    fi
}

# 比較 nm 和 GDB 輸出
symcompare() {
    local file="$1"
    local func="${2:-main}"
    
    echo "=== nm output ==="
    nm -DC "$file" | grep "$func"
    
    echo -e "\n=== GDB output ==="
    gdb "$file" -batch -ex "info functions $func" 2>/dev/null | grep -v "^$"
}

# 快速分析函式庫（結合使用）
libanalyze() {
    local lib="$1"
    
    echo "=== Quick Symbol Check (nm) ==="
    echo "Exported functions: $(nm -D "$lib" 2>/dev/null | grep -c " T ")"
    echo "Undefined symbols: $(nm -u "$lib" 2>/dev/null | wc -l)"
    
    echo -e "\n=== Top 5 Functions (nm) ==="
    nm -DC "$lib" 2>/dev/null | grep " T " | head -5
    
    echo -e "\n=== Detailed Analysis (GDB) ==="
    # 只對第一個函數做詳細分析
    local first_func=$(nm -DC "$lib" 2>/dev/null | grep " T " | head -1 | awk '{print $3}')
    if [[ -n "$first_func" ]]; then
        echo "Details of $first_func:"
        gdb "$lib" -batch -ex "info functions ^${first_func}$" 2>/dev/null | grep -v "^$"
    fi
}
```

### 搜尋函數
```bash
# ~/.bashrc
sofind() {
    local pattern="$1"
    shift
    
    for file in "$@"; do
        echo "=== $file ==="
        gdb "$file" -batch -ex "info functions $pattern" 2>/dev/null | \
            grep -E "^0x[0-9a-f]+"
    done
}

# 使用方式
# sofind "init" *.so
```

## 批次處理技巧

### 13. 分析多個檔案
```bash
# 批次檢查所有 .so 的函數
for lib in *.so; do
    echo "=== $lib ==="
    gdb "$lib" -batch -ex "info functions" | head -10
done

# 找出包含特定函數的函式庫
for lib in /usr/lib/*.so; do
    if gdb "$lib" -batch -ex "info functions pthread_create" 2>/dev/null | grep -q pthread_create; then
        echo "$lib contains pthread_create"
    fi
done
```

### 14. 產生報告
```bash
#!/bin/bash
# analyze_lib.sh
generate_report() {
    local lib="$1"
    local output="${lib%.so}_report.txt"
    
    {
        echo "Library Analysis Report: $lib"
        echo "Generated: $(date)"
        echo "================================"
        
        echo -e "\n## Functions"
        gdb "$lib" -batch -ex "info functions" | head -20
        
        echo -e "\n## Global Variables"
        gdb "$lib" -batch -ex "info variables" | head -20
        
        echo -e "\n## Dependencies"
        ldd "$lib"
        
        echo -e "\n## Security Features"
        checksec --file="$lib" 2>/dev/null || echo "checksec not installed"
        
    } > "$output"
    
    echo "Report saved to: $output"
}
```

## 除錯技巧

### 15. 設定斷點和追蹤
```bash
# 在函式庫載入時設定斷點
gdb ./main_program -batch \
    -ex "set breakpoint pending on" \
    -ex "break lib.so:function_name" \
    -ex "run" \
    -ex "backtrace"

# 追蹤函數呼叫
gdb ./program -batch \
    -ex "set pagination off" \
    -ex "break function_name" \
    -ex "commands" \
    -ex "silent" \
    -ex "backtrace 1" \
    -ex "continue" \
    -ex "end" \
    -ex "run"
```

## nm vs GDB 詳細比較

### 核心差異
```bash
# nm - 簡單快速的符號查看器
nm lib.so              # 列出所有符號
nm -D lib.so           # 只看動態符號
nm -C lib.so           # Demangle C++ 符號

# GDB - 功能強大的分析器
gdb lib.so -batch -ex "info functions"     # 不只是符號
gdb lib.so -batch -ex "disassemble func"   # 還能反組譯
gdb lib.so -batch -ex "ptype struct"       # 查看資料結構
```

### 功能對比表

| 功能 | nm | GDB | 說明 |
|------|-----|-----|------|
| **查看符號** | ✅ 快速 | ✅ 詳細 | nm 更快，GDB 資訊更多 |
| **過濾功能** | 需要 grep | ✅ 內建正則 | GDB 可直接過濾 |
| **反組譯** | ❌ | ✅ | 只有 GDB 能反組譯 |
| **查看資料結構** | ❌ | ✅ | GDB 能顯示 struct/class 定義 |
| **除錯資訊** | 部分 | ✅ 完整 | GDB 能讀取完整除錯資訊 |
| **執行時分析** | ❌ | ✅ | GDB 能動態除錯 |
| **速度** | ✅ 極快 | 較慢 | nm 專門設計用來快速查看 |
| **輸出格式** | 簡潔 | 詳細 | nm 輸出更適合腳本處理 |

### 實際範例比較

#### 查看函數符號
```bash
# nm - 簡潔輸出
$ nm -D lib.so | grep " T "
0000000000001140 T init_library
0000000000001260 T process_data

# GDB - 詳細資訊
$ gdb lib.so -batch -ex "info functions init"
0x0000000000001140  init_library(int, char**)
0x0000000000001260  init_config(void)
```

#### C++ 符號處理
```bash
# nm - 需要 -C 來 demangle
$ nm lib.so
00001234 T _ZN7MyClass10myFunctionEv  # 難讀

$ nm -C lib.so  
00001234 T MyClass::myFunction()      # 易讀

# GDB - 自動處理，還能看參數類型
$ gdb lib.so -batch -ex "info functions MyClass"
0x00001234  MyClass::myFunction()
0x00001456  MyClass::MyClass(int, std::string const&)
```

#### 符號類型識別
```bash
# nm - 用字母表示類型
$ nm lib.so
0000000000001140 T init_library    # T = Text (code)
0000000000004020 D global_var      # D = Data
0000000000004040 B uninit_var      # B = BSS
                 U printf           # U = Undefined

# GDB - 分類顯示
$ gdb lib.so -batch -ex "info functions"   # 只看函數
$ gdb lib.so -batch -ex "info variables"   # 只看變數
```

### nm 符號類型代碼表

| 代碼 | 意義 | 說明 |
|------|------|------|
| **T/t** | Text (code) | 程式碼段的符號 (大寫=全域，小寫=局部) |
| **D/d** | Data | 已初始化資料段 |
| **B/b** | BSS | 未初始化資料段 |
| **R/r** | Read-only | 唯讀資料段 |
| **W/w** | Weak | 弱符號 |
| **U** | Undefined | 未定義符號（需要外部連結） |
| **A** | Absolute | 絕對符號 |
| **C** | Common | 共同符號 |
| **N** | Debug | 除錯符號 |

### 效能比較
```bash
# 測試大型函式庫 (如 libc.so)
$ time nm -D /lib/x86_64-linux-gnu/libc.so.6 > /dev/null
real    0m0.012s

$ time gdb /lib/x86_64-linux-gnu/libc.so.6 -batch -ex "info functions" > /dev/null  
real    0m0.283s

# nm 快約 20 倍！
```

### 什麼時候用哪個？

#### 使用 nm 的場景
```bash
# 1. 快速檢查符號是否存在
nm -D lib.so | grep function_name

# 2. 批量處理多個檔案
for lib in *.so; do
    nm -D "$lib" | grep -q "init" && echo "$lib has init"
done

# 3. 產生符號列表
nm -D lib.so > symbols.txt

# 4. 檢查未定義符號
nm -u lib.so

# 5. 腳本自動化
nm lib.so | awk '$2=="T" {print $3}' | sort
```

#### 使用 GDB 的場景
```bash
# 1. 需要看函數參數和返回類型
gdb lib.so -batch -ex "info functions process"

# 2. 查看資料結構定義
gdb lib.so -batch -ex "ptype struct config_data"

# 3. 反組譯分析
gdb lib.so -batch -ex "disassemble critical_function"

# 4. 複雜的正則過濾
gdb lib.so -batch -ex "info functions ^lib_.*_init$"

# 5. 需要除錯資訊
gdb lib.so -batch -ex "info sources"
```

## 其他相關工具比較

| 工具 | 優點 | 使用場景 | 速度 |
|------|------|----------|------|
| `nm` | 快速、簡單 | 快速查看符號 | ⚡ 極快 |
| `objdump` | 功能全面 | 查看段、反組譯 | 🚀 快 |
| `readelf` | ELF 格式專用 | 詳細 ELF 分析 | 🚀 快 |
| `ldd` | 依賴關係 | 查看動態連結 | ⚡ 極快 |
| `strings` | 提取字串 | 查找硬編碼字串 | ⚡ 極快 |
| `gdb` | 最強大 | 深度分析、除錯 | 🐢 較慢 |

## 常見問題解決

### 符號被剝離（stripped）
```bash
# 檢查是否被剝離
file lib.so

# 嘗試從除錯符號包載入
gdb lib.so -batch -ex "symbol-file lib.so.debug" -ex "info functions"
```

### 檢查 32/64 位元
```bash
gdb lib.so -batch -ex "show architecture"
```

### 查看編譯器優化等級
```bash
# 通過反組譯推測
gdb lib.so -batch -ex "disassemble main" | grep -E "(nop|lea.*\[.*\+0\])"
```

## 快速決策指南

### 選擇工具的決策樹
```
需要分析 .so/.a 檔案？
├── 只要看符號名稱？ → 用 nm
├── 需要看函數參數？ → 用 GDB
├── 需要反組譯？ → 用 GDB 或 objdump
├── 需要看資料結構？ → 用 GDB
├── 批量處理多檔案？ → 用 nm + 腳本
└── 深度除錯分析？ → 用 GDB
```

### 總結比較

| 需求 | 最佳工具 | 指令範例 |
|------|----------|----------|
| **快速查看符號** | nm | `nm -DC lib.so \| grep func` |
| **檢查未定義符號** | nm | `nm -u lib.so` |
| **查看函數簽名** | GDB | `gdb lib.so -batch -ex "info functions"` |
| **反組譯函數** | GDB | `gdb lib.so -batch -ex "disas func"` |
| **查看結構定義** | GDB | `gdb lib.so -batch -ex "ptype struct"` |
| **批量檢查** | nm | `for f in *.so; do nm -D $f; done` |
| **C++ 符號** | 兩者皆可 | `nm -C` 或 GDB 自動處理 |
| **效能優先** | nm | nm 比 GDB 快 20+ 倍 |
| **資訊完整** | GDB | GDB 提供最詳細資訊 |

### 一句話總結
- **nm** = 瑞士刀（輕巧快速，適合日常查看）
- **GDB** = 工具箱（功能齊全，適合深度分析）
- **最佳實踐** = 先用 nm 快速篩選，再用 GDB 深入分析