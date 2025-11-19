# Rust Callstack 介紹

## 專案概述
`rust_callstack_demo` 是一個展示 Rust 程式執行時函式呼叫堆疊（callstack）追蹤技術的示範專案。透過 `backtrace` crate，能夠在程式執行時動態捕捉並顯示函式的呼叫鏈路，對於除錯、效能分析和理解程式執行流程非常有幫助。

## 專案結構
```
rust_callstack_demo/
├── Cargo.toml           # 專案配置文件
├── src/
│   ├── main.rs         # 主程式：展示基本的呼叫追蹤功能
│   └── lib.rs          # 函式庫：提供測試用的追蹤巨集
└── examples/
    └── auto_trace.rs   # 進階範例：自動化追蹤系統
```

## 核心功能特性

### 1. 函式呼叫追蹤
- **動態堆疊捕捉**：在執行時即時捕捉當前的函式呼叫堆疊
- **呼叫者識別**：自動識別並顯示呼叫當前函式的上層函式名稱
- **縮排層級顯示**：透過縮排視覺化呈現呼叫深度

### 2. 智慧過濾機制
程式實作了智慧的堆疊框架過濾，自動排除系統和框架相關的呼叫：
- 標準庫函式（`std::`、`core::`）
- Backtrace 相關函式
- 系統啟動函式（`_start`、`__libc_start`）
- 編譯器生成的雜湊函式名稱

### 3. 巨集系統

#### `trace_call!` / `auto_trace!`
進入函式時記錄呼叫資訊：
```rust
fn function_a() {
    trace_call!("function_a");  // 記錄進入函式
    // 函式邏輯...
}
```

#### `trace_exit!` / `trace_return!`
離開函式時調整縮排層級：
```rust
fn function_b() {
    auto_trace!();
    // 函式邏輯...
    trace_return!();  // 記錄離開函式
}
```

## 技術實現細節

### 1. Backtrace 整合
使用 `backtrace` crate 捕捉執行時堆疊：
```rust
let bt = Backtrace::new();
let frames = bt.frames();
```

### 2. 符號解析
從堆疊框架中提取函式名稱：
```rust
for symbol in frame.symbols() {
    if let Some(name) = symbol.name() {
        // 解析並處理函式名稱
    }
}
```

### 3. 全域狀態管理
使用 `Mutex` 保護全域縮排層級，確保執行緒安全：
```rust
static INDENT_LEVEL: Mutex<usize> = Mutex::new(0);
```

### 4. 測試框架整合
提供專門的測試巨集 `test_trace_call!`，配合 `once_cell` 實現測試輸出收集：
```rust
pub static TEST_OUTPUT: Lazy<Mutex<Vec<String>>> = 
    Lazy::new(|| Mutex::new(Vec::new()));
```

## 使用範例

### 基本使用（main.rs）
```rust
fn main() {
    function_a();  // 開始追蹤呼叫鏈
}

fn function_a() {
    trace_call!("function_a");
    function_b();
    trace_exit!();
}
```

輸出效果：
```
→ Entering: function_a (called from: main)
    Executing function_a
  → Entering: function_b (called from: function_a)
      Executing function_b
    → Entering: function_c (called from: function_b)
        Executing function_c
```

### 遞迴追蹤
支援遞迴函式的呼叫追蹤：
```rust
fn recursive_function(depth: u32) {
    trace_call!("recursive_function");
    if depth > 0 {
        recursive_function(depth - 1);
    }
    trace_exit!();
}
```

### 自動化追蹤（auto_trace.rs）
提供更智慧的自動追蹤功能，自動提取當前函式名稱：
```rust
fn calculate_factorial(n: u32) -> u32 {
    auto_trace!();  // 自動獲取函式名稱
    let result = if n <= 1 {
        1
    } else {
        n * calculate_factorial(n - 1)
    };
    trace_return!();
    result
}
```

## 測試覆蓋

專案包含完整的單元測試，驗證：
1. **基本呼叫鏈追蹤**：確認函式呼叫順序正確記錄
2. **遞迴呼叫追蹤**：驗證遞迴函式的多層呼叫
3. **直接呼叫追蹤**：測試從測試函式直接呼叫的情況

測試執行：
```bash
cargo test
```

## 應用場景

### 1. 除錯輔助
- 快速定位函式呼叫路徑
- 理解複雜的呼叫關係
- 發現意外的呼叫模式

### 2. 效能分析
- 識別熱點函式路徑
- 分析呼叫深度
- 優化呼叫鏈

### 3. 程式碼理解
- 新手快速理解程式執行流程
- 文件化實際的執行路徑
- 驗證設計假設

### 4. 測試驗證
- 確認函式呼叫順序符合預期
- 驗證邊界條件下的執行路徑
- 自動化測試的輔助工具

## 依賴套件
- **backtrace** (0.3)：提供堆疊追蹤功能
- **once_cell** (1.19)：用於延遲初始化的靜態變數

## 編譯與執行

### 執行主程式
```bash
cargo run
```

### 執行範例程式
```bash
cargo run --example auto_trace
```

### 執行測試
```bash
cargo test
```

## 技術優勢

1. **零成本抽象**：使用巨集在編譯時展開，執行時開銷最小
2. **執行緒安全**：使用 Mutex 保護共享狀態
3. **靈活可擴展**：巨集系統易於客製化和擴展
4. **測試友好**：專門的測試巨集支援自動化測試

## 潛在改進方向

1. **效能優化**
   - 實作無鎖的縮排層級管理
   - 快取符號解析結果
   - 條件編譯支援（僅在 debug 模式啟用）

2. **功能增強**
   - 支援非同步函式追蹤
   - 添加時間戳記
   - 整合日誌系統
   - 支援輸出到檔案

3. **視覺化改進**
   - 彩色輸出支援
   - 圖形化呼叫樹生成
   - 即時追蹤視圖

## 結論

`rust_callstack_demo` 專案展示瞭如何在 Rust 中實現強大的函式呼叫追蹤系統。透過結合 `backtrace` crate 和巧妙的巨集設計，提供了一個既實用又高效的除錯工具。這個專案不僅是學習 Rust 堆疊追蹤技術的絕佳範例，也可以作為實際專案中除錯和效能分析的基礎工具。

專案程式碼簡潔清晰，測試完善，是理解 Rust 系統程式設計和除錯技術的優秀教材。透過這個專案，開發者可以深入理解：
- Rust 的堆疊追蹤機制
- 巨集系統的實際應用
- 全域狀態的安全管理
- 測試驅動開發的實踐
