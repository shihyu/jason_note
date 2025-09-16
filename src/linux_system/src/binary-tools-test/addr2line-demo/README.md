# addr2line 測試示例

本目錄包含 addr2line 工具的完整測試範例，用於驗證地址到源碼映射功能。

## 文件說明

- `segfault_demo.c` - 段錯誤演示程序，展示如何使用 addr2line 調試崩潰
- `backtrace_demo.c` - 調用棧追蹤演示，自動生成 addr2line 命令
- `cpp_demo.cpp` - C++ 程序演示，測試 C++ 符號 demangling
- `test_addr2line.sh` - 自動化測試腳本
- `Makefile` - 構建配置

## 快速開始

### 1. 編譯所有程序
```bash
make all
```

### 2. 運行自動化測試
```bash
make test
# 或直接運行
./test_addr2line.sh
```

### 3. 查看函數地址
```bash
make show-addresses
```

## 使用範例

### 基本用法
```bash
# 獲取函數地址
nm segfault_demo | grep main

# 解析地址
addr2line -fe segfault_demo 0x400534
```

### 段錯誤調試
```bash
# 運行會崩潰的程序
./segfault_demo --crash

# 從 dmesg 獲取崩潰地址
dmesg | grep segfault

# 解析崩潰地址
addr2line -Cfpe segfault_demo 0x[crash_address]
```

### 調用棧分析
```bash
# 生成調用棧
./backtrace_demo 2

# 批量解析地址
./backtrace_demo 1 | grep "^0x" | xargs addr2line -Cfpe backtrace_demo
```

### C++ 符號處理
```bash
# 測試 C++ demangling
./cpp_demo 4

# 解析 C++ 符號（帶 demangling）
addr2line -Cfpe cpp_demo [address]
```

## 測試覆蓋範圍

- ✅ 基本地址解析
- ✅ 多地址批量處理
- ✅ C++ 符號 demangling
- ✅ 管道輸入支持
- ✅ 優雅格式輸出 (-p)
- ✅ 調用棧追蹤
- ✅ 內聯函數處理
- ✅ objdump 集成
- ✅ 錯誤處理
- ✅ 崩潰分析模擬

## 常用 addr2line 選項

| 選項 | 說明 |
|------|------|
| -e | 指定可執行文件 |
| -f | 顯示函數名 |
| -C | Demangle C++ 符號 |
| -s | 簡短文件名 |
| -p | 優雅格式輸出 |
| -i | 顯示內聯函數 |
| -a | 顯示地址 |

## 故障排除

1. **找不到源碼位置**
   - 確保使用 -g 編譯選項
   - 檢查二進制文件是否被 strip

2. **C++ 符號亂碼**
   - 使用 -C 選項進行 demangling

3. **地址解析失敗**
   - 確認地址格式正確（0x開頭）
   - 檢查地址是否在程序範圍內

## 清理
```bash
make clean
```