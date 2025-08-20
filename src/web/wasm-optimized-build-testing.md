# 測試優化後的 WASM 文件完整指南

## 1. 環境準備

### 安裝必要工具

```bash
# 安裝 wasm-pack
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# 安裝 wasm-opt (Binaryen)
# Ubuntu/Debian
sudo apt install binaryen
# macOS
brew install binaryen
# Windows
scoop install binaryen

# 添加 WASM 目標
rustup target add wasm32-unknown-unknown
```

---

## 2. Rust 項目設置

### Cargo.toml 配置

```toml
[package]
name = "my-wasm-project"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
js-sys = "0.3"

[dependencies.web-sys]
version = "0.3"
features = ["console", "Performance"]

[profile.release]
lto = true
opt-level = 3
codegen-units = 1
```

### 帶日誌的 Rust 源碼 (src/lib.rs)

```rust
use wasm_bindgen::prelude::*;

// 導入 console API
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)] fn log(s: &str);
    #[wasm_bindgen(js_namespace = console)] fn error(s: &str);
    #[wasm_bindgen(js_namespace = console)] fn warn(s: &str);
    #[wasm_bindgen(js_namespace = console)] fn info(s: &str);
    #[wasm_bindgen(js_namespace = console, js_name = time)] fn console_time(s: &str);
    #[wasm_bindgen(js_namespace = console, js_name = timeEnd)] fn console_time_end(s: &str);
}

// 日誌宏
macro_rules! console_log { ($($t:tt)*) => (log(&format!("[WASM LOG] {}", format_args!($($t)*)))) }
macro_rules! console_error { ($($t:tt)*) => (error(&format!("[WASM ERROR] {}", format_args!($($t)*)))) }
macro_rules! console_warn { ($($t:tt)*) => (warn(&format!("[WASM WARN] {}", format_args!($($t)*)))) }
macro_rules! console_info { ($($t:tt)*) => (info(&format!("[WASM INFO] {}", format_args!($($t)*)))) }

// 初始化函數
#[wasm_bindgen(start)]
pub fn main() {
    console_log!("WASM 模組已載入，版本: optimized");
}

// 基本測試函數
#[wasm_bindgen]
pub fn test_basic_math(a: i32, b: i32) -> i32 {
    console_log!("執行基本數學運算: {} + {}", a, b);
    let result = a + b;
    console_log!("結果: {}", result);
    result
}
```

👉 其餘函數包含 **字符串處理**、**重計算**、**數組處理**、**錯誤處理**、**性能基準測試**、**內存信息**，完整程式碼已在原始內容中。

---

## 3. 編譯和優化

### 自動化構建腳本 (build\_and\_optimize.sh)

```bash
#!/bin/bash
echo "=== 開始 Rust WASM 編譯流程 ==="

# 清理舊文件
rm -rf pkg/
rm -f *.wasm

# 編譯 WASM
echo "步驟 1: 編譯 Rust 到 WASM..."
wasm-pack build --target web --out-dir pkg --release
if [ $? -ne 0 ]; then
  echo "❌ 編譯失敗"
  exit 1
fi
echo "✅ 編譯成功"

# 獲取原始文件大小
ORIGINAL_SIZE=$(wc -c < pkg/*_bg.wasm)
echo "原始 WASM 大小: $ORIGINAL_SIZE bytes"

# 優化 WASM
echo "步驟 2: 優化 WASM 文件..."
wasm-opt -Oz --enable-bulk-memory --enable-sign-ext \
  -o pkg/optimized.wasm pkg/*_bg.wasm
if [ $? -ne 0 ]; then
  echo "❌ 優化失敗"
  exit 1
fi

# 獲取優化後文件大小
OPTIMIZED_SIZE=$(wc -c < pkg/optimized.wasm)
REDUCTION=$((ORIGINAL_SIZE - OPTIMIZED_SIZE))
PERCENTAGE=$(echo "scale=2; $REDUCTION * 100 / $ORIGINAL_SIZE" | bc)

echo "✅ 優化完成"
echo "優化後大小: $OPTIMIZED_SIZE bytes"
echo "減少: $REDUCTION bytes ($PERCENTAGE%)"

# 生成測試報告
echo "步驟 3: 生成文件信息..."
echo "=== WASM 文件信息 ===" > wasm_info.txt
echo "編譯時間: $(date)" >> wasm_info.txt
echo "原始大小: $ORIGINAL_SIZE bytes" >> wasm_info.txt
echo "優化大小: $OPTIMIZED_SIZE bytes" >> wasm_info.txt
echo "壓縮率: $PERCENTAGE%" >> wasm_info.txt

echo "✅ 構建完成！"
```

### 常用優化命令選項

```bash
# 基本優化
wasm-opt -O3 -o optimized.wasm original.wasm

# 最小化大小
wasm-opt -Oz -o optimized.wasm original.wasm

# 速度優化
wasm-opt -O4 -o optimized.wasm original.wasm

# 詳細輸出
wasm-opt -Oz --enable-bulk-memory --enable-sign-ext \
  -o optimized.wasm original.wasm -v
```

---

## 4. JavaScript 測試代碼

* **完整版測試** → \[test.js]
* **簡化測試** (simple\_test.js)：

```javascript
import init, { test_basic_math, get_memory_info } from './pkg/my_wasm_project.js';

async function simpleTest() {
  console.log('開始簡單測試...');
  try {
    await init('./pkg/optimized.wasm');
    console.log('✅ WASM 載入成功');

    const mathResult = test_basic_math(10, 20);
    console.log(`數學測試結果: ${mathResult}`);

    const memInfo = get_memory_info();
    console.log(`內存信息: ${memInfo}`);

    console.log('✅ 所有測試通過');
  } catch (error) {
    console.error('❌ 測試失敗:', error);
  }
}
simpleTest();
```

---

## 5. 運行和測試

### 執行構建

```bash
chmod +x build_and_optimize.sh
./build_and_optimize.sh
```

### 啟動服務器

```bash
# 方法 1: Python
python3 -m http.server 8080

# 方法 2: Node.js
npx serve . -p 8080

# 方法 3: Rust
cargo install basic-http-server
basic-http-server . -a 0.0.0.0:8080
```

### 瀏覽器測試

```javascript
import('./test.js').then(testModule => {
  testModule.testBasicMath();
  testModule.runAllTests();
  console.log(testModule.logger.getLogs());
  console.log(testModule.monitor.getMetrics());
});
```

---

## 6. 調試和分析工具

### WASM 文件分析命令

```bash
wasm-objdump -h optimized.wasm     # 文件結構
wasm-objdump -j Export optimized.wasm  # 導出函數
wasm-objdump -j Import optimized.wasm  # 導入函數
wasm2wat optimized.wasm -o optimized.wat # 轉 wat
wasm-validate optimized.wasm       # 驗證完整性
wasm-objdump -x optimized.wasm     # 詳細信息
wasm-objdump -j Function optimized.wasm # 函數簽名
```

### 性能分析腳本 (perf\_analysis.js)

（可進行函數多次迭代測量，輸出 min/max/mean/95p/99p）

---

## 7. 常見問題排查

### 編譯問題

```bash
rustc --version
wasm-pack --version
cargo clean
wasm-pack build --target web --release
cargo check
```

### 優化問題

```bash
wasm-opt --version
ls -la pkg/*_bg.wasm
wasm-opt -O1 -o test1.wasm pkg/*_bg.wasm
wasm-opt -O2 -o test2.wasm pkg/*_bg.wasm
wasm-opt -O3 -o test3.wasm pkg/*_bg.wasm
wasm-opt -Oz -o test4.wasm pkg/*_bg.wasm
ls -la test*.wasm
```
