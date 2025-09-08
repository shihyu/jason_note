# FFI 跨語言程式設計範例

這個目錄包含了完整的 FFI (Foreign Function Interface) 範例，展示如何在 C/C++、Rust 和 Python 之間進行跨語言調用。

## 目錄結構

```
ffi_examples/
├── c_libs/              # C/C++ 函式庫
│   ├── math_lib.c      # C 函式庫實作
│   ├── math_lib.h      # C 函式庫標頭檔
│   └── cpp_wrapper.cpp # C++ 封裝與擴展
├── python/              # Python 範例
│   ├── python_ffi.py        # Python 調用 C
│   ├── python_call_rust.py  # Python 調用 Rust
│   └── python_call_cpp.py   # Python 調用 C++
├── rust_libs/           # Rust 程式
│   ├── rust_ffi/       # Rust 調用 C 範例
│   └── rust_lib/       # Rust 函式庫供其他語言調用
├── Makefile            # 自動化編譯腳本
└── README.md           # 本文件
```

## 快速開始

### 前置需求

- GCC/G++ 編譯器
- Rust 和 Cargo
- Python 3.x
- Make 工具

### 編譯和測試

```bash
# 編譯所有函式庫並執行測試
make all

# 只編譯
make build

# 只測試
make test

# 清理編譯產物
make clean

# 查看幫助
make help
```

## 範例說明

### 1. C 函式庫 (math_lib)
提供基礎數學運算、字串處理和結構體操作：
- 加法、階乘、斐波那契數
- 字串反轉、問候語
- 陣列總和計算
- 點結構體和曼哈頓距離計算

### 2. Python 調用 C (python_ffi.py)
展示如何使用 ctypes 調用 C 函式：
- 基本數值運算
- 字串處理（包括可修改字串）
- 陣列操作
- 結構體使用

### 3. Rust 調用 C (rust_ffi)
展示 Rust 的 FFI 功能：
- 使用 extern "C" 聲明外部函數
- 處理 C 字串（CString/CStr）
- 陣列和結構體互操作
- 安全和不安全代碼邊界

### 4. Rust 函式庫 (rust_lib)
創建可被其他語言調用的 Rust 函式庫：
- 使用 #[no_mangle] 導出函數
- 字串記憶體管理
- 向量運算
- UTF-8 字元計數

### 5. C++ 封裝 (cpp_wrapper)
展示 C++ 與 C 的互操作：
- Calculator 類別封裝
- 字串處理工具
- 混合使用 C 和 C++ 功能
- 陣列排序等進階功能

## 測試輸出範例

執行 `make test` 會看到類似以下的輸出：

```
執行 Python 調用 C 測試...
================================
Python FFI 範例 - 調用 C 函數庫

=== 測試基本數學運算 ===
add(10, 20) = 30
factorial(5) = 120
fibonacci(10) = 55
✓ 基本數學運算測試通過

[更多測試輸出...]

================================
✅ 所有 FFI 測試通過！
================================
```

## 注意事項

1. **函式庫路徑**：執行時需要正確設置動態函式庫路徑
2. **記憶體管理**：跨語言邊界時要特別注意記憶體的分配和釋放
3. **字串編碼**：Python 字串需要編碼為 bytes，Rust 需要處理 UTF-8
4. **錯誤處理**：FFI 邊界不能傳遞異常，需要使用錯誤碼

## 延伸學習

- 瞭解 C ABI 的重要性
- 學習各語言的類型映射
- 掌握記憶體管理原則
- 處理複雜數據結構的傳遞

## 故障排除

如果遇到函式庫載入錯誤：

1. 確認已執行 `make build` 編譯所有函式庫
2. 檢查動態函式庫路徑設置
3. 在 Linux/macOS 上可能需要設置 `LD_LIBRARY_PATH`
4. 確認所有依賴都已安裝（gcc, g++, rust, python3）

## 授權

本範例代碼僅供學習使用。