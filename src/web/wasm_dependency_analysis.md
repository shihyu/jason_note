# wasm-objdump 分析指南：深入 WASM 檔案與 Buttplug 依賴解析

## 🎯 核心問題解答

**問題**：`buttplug_server_bg.wasm` 會包含 `dependencies` 中的 `buttplug` 函數嗎？

**答案**：**會的！** 但不是全部，只包含實際使用到的函數。

---

## 🔍 包含機制說明

### ✅ 會被包含的 Buttplug 函數

- 你的程式碼**直接調用**的函數
- 被調用函數所**依賴**的函數  
- Rust 編譯器**無法消除**的函數

### ❌ 不會被包含的 Buttplug 函數

- 你沒有使用的函數（Dead Code Elimination）
- `default-features = false` 排除的功能
- 非 `wasm` feature 的功能

---

## 📊 根據程式碼分析實際包含內容

### 從 `lib.rs` 分析

```rust
// 這些 Buttplug 函數會被包含在 WASM 中：
use buttplug::{
  core::message::{ButtplugCurrentSpecServerMessage, serializer::vec_to_protocol_json},  // ✅
  server::ButtplugServer,  // ✅
  util::async_manager,     // ✅
  server::ButtplugServerBuilder,  // ✅
  core::message::{BUTTPLUG_CURRENT_MESSAGE_SPEC_VERSION, serializer::{...}}  // ✅
};

// 實際調用的函數：
vec_to_protocol_json()                    // ✅ 會包含
ButtplugServerBuilder::default()          // ✅ 會包含
builder.finish()                          // ✅ 會包含
server.event_stream()                     // ✅ 會包含
server.parse_message()                    // ✅ 會包含
ButtplugServerJSONSerializer::default()   // ✅ 會包含
async_manager::spawn()                    // ✅ 會包含
```

### 從 `webbluetooth_manager.rs` 分析

```rust
// 這些也會被包含：
use buttplug::{
  server::device::hardware::communication::*,  // ✅ 使用到的部分
  util::device_configuration::create_test_dcm, // ✅ 會包含
};

// 實際調用：
create_test_dcm(false)                           // ✅ 會包含
config_manager.protocol_device_configurations() // ✅ 會包含
HardwareCommunicationManagerEvent::DeviceFound  // ✅ 會包含
```

### 從 `webbluetooth_hardware.rs` 分析

```rust
// 實作的 Buttplug traits 和使用的類型：
impl HardwareConnector for WebBluetoothHardwareConnector     // ✅ trait 實作
impl HardwareSpecializer for WebBluetoothHardwareSpecializer // ✅ trait 實作  
impl HardwareInternal for WebBluetoothHardware               // ✅ trait 實作

// 調用的函數：
BluetoothLESpecifier::new_from_device()    // ✅ 會包含
Hardware::new()                            // ✅ 會包含
HardwareReading::new()                     // ✅ 會包含
HardwareEvent::Disconnected()             // ✅ 會包含
HardwareEvent::Notification()             // ✅ 會包含
```

---

## 📈 WASM 檔案組成估算

```
buttplug_server_bg.wasm (假設 2-5 MB)
├── 你的程式碼 (~5-10%)
├── Buttplug 核心功能 (~40-60%)
│   ├── 訊息序列化/反序列化
│   ├── 伺服器邏輯
│   ├── 設備管理
│   └── 藍牙通訊
├── 第三方依賴 (~20-30%)
│   ├── serde (序列化)
│   ├── tokio (異步運行時)
│   ├── futures (Future trait)
│   └── 其他...
├── Rust 標準庫 (~10-20%)
└── wasm-bindgen 綁定 (~5-10%)
```

---

## 🚨 重要提醒：優化等級對分析的影響

### ⚠️ 關鍵注意事項

**WASM 分析的成功關鍵在於使用正確的建置模式！**

```bash
# ✅ 正確：用於分析和除錯
wasm-pack build --dev --target web

# ❌ 錯誤：用於分析時會找不到函數
wasm-pack build --release --target web
```

**為什麼這很重要？**
- `--dev` 模式：保留所有函數名稱和符號，類似 GCC `-O0`
- `--release` 模式：大量優化、內聯、移除未使用函數，類似 GCC `-O3`

### 📊 建置模式比較

| 建置模式 | 函數可見性 | 檔案大小 | 適用場景 |
|----------|------------|----------|----------|
| `--dev` | 🟢 幾乎所有函數可見 | 🔴 大 (8-15MB) | 分析、除錯、學習 |
| `--release` | 🔴 大量函數被優化掉 | 🟢 小 (2-5MB) | 生產部署 |

### 🔧 安裝 wasm-objdump

#### macOS
```bash
brew install wabt
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install wabt
```

#### Windows
```bash
# 使用 Chocolatey
choco install wabt

# 使用 Scoop
scoop install wabt
```

#### 從源碼編譯
```bash
git clone --recursive https://github.com/WebAssembly/wabt
cd wabt
mkdir build && cd build
cmake ..
cmake --build .

# 將編譯出的工具加入 PATH
export PATH=$PWD:$PATH
```

#### 驗證安裝
```bash
wasm-objdump --version
# 應該顯示：wasm-objdump 1.x.x
```

---

## 🔍 實際驗證方法

### ⚡ 第一步：使用正確的建置模式

```bash
# 🎯 關鍵步驟：必須使用 --dev 模式進行分析
wasm-pack build --dev --target web --out-dir pkg-debug
```

### 1. 查看包含的 Buttplug 相關函數

```bash
# 查看所有包含 buttplug 的符號
strings pkg-debug/buttplug_server_bg.wasm | grep -i buttplug

# 查看反組譯中的 buttplug 函數
wasm-objdump -d pkg-debug/buttplug_server_bg.wasm | grep -i buttplug

# 查看 WAT 格式中的 buttplug 函數
wasm2wat pkg-debug/buttplug_server_bg.wasm | grep -i buttplug
```

### 2. 分析函數大小和依賴

```bash
# 安裝並使用 twiggy 分析
cargo install twiggy

# 查看最大的函數（可能包含 buttplug 函數）
twiggy top pkg-debug/buttplug_server_bg.wasm

# 查看包含 buttplug 的函數
twiggy top pkg-debug/buttplug_server_bg.wasm | grep -i buttplug

# 查看特定函數的依賴
twiggy dominators pkg-debug/buttplug_server_bg.wasm | grep -i buttplug
```

### 3. 完整分析指令集

```bash
# 🎯 重要：確保使用 --dev 建置的版本進行分析

# 1. 查看字串中的 Buttplug 相關內容
strings pkg-debug/buttplug_server_bg.wasm | grep -E "(buttplug|Buttplug)" | sort

# 2. 查看反組譯中的函數名稱
wasm-objdump -d pkg-debug/buttplug_server_bg.wasm | grep -E "func.*buttplug" 

# 3. 轉換為 WAT 格式查看
wasm2wat pkg-debug/buttplug_server_bg.wasm -o temp.wat
grep -E "(buttplug|Buttplug)" temp.wat

# 4. 使用 twiggy 分析大小
twiggy top pkg-debug/buttplug_server_bg.wasm | head -20

# 5. 查看匯出/匯入函數
wasm-objdump -x pkg-debug/buttplug_server_bg.wasm | grep -A 20 "Export\["
wasm-objdump -x pkg-debug/buttplug_server_bg.wasm | grep -A 50 "Import\["
```

### ⚠️ 對比：Release 模式的差異

```bash
# 建立 release 版本對比
wasm-pack build --release --target web --out-dir pkg-release

# 比較函數數量差異
echo "Debug 版本函數數量："
wasm-objdump -x pkg-debug/buttplug_server_bg.wasm | grep -c "func\["

echo "Release 版本函數數量："
wasm-objdump -x pkg-release/buttplug_server_bg.wasm | grep -c "func\["

# 比較 Buttplug 相關字串
echo "Debug 版本 Buttplug 字串："
strings pkg-debug/buttplug_server_bg.wasm | grep -c buttplug

echo "Release 版本 Buttplug 字串："
strings pkg-release/buttplug_server_bg.wasm | grep -c buttplug

# 比較檔案大小
ls -lh pkg-*/buttplug_server_bg.wasm
```

**預期差異**：
```
Debug 版本函數數量：2847
Release 版本函數數量：634

Debug 版本 Buttplug 字串：156  
Release 版本 Buttplug 字串：23

-rw-r--r-- 1 user user  12M pkg-debug/buttplug_server_bg.wasm
-rw-r--r-- 1 user user 2.5M pkg-release/buttplug_server_bg.wasm
```

---

## 📋 預期分析結果

### strings 輸出可能包含：

```
ButtplugServer
ButtplugServerBuilder  
ButtplugCurrentSpecServerMessage
ButtplugDeviceError
buttplug::server::
buttplug::core::message::
WebBluetoothCommunicationManager
HardwareCommunicationManager
HardwareConnector
```

### twiggy 輸出可能顯示：

```
 Shallow Bytes │ Shallow % │ Item
───────────────┼───────────┼────────────────────────────────────
        45,231 │     2.84% │ buttplug::server::ButtplugServer::new
        32,156 │     2.02% │ buttplug::core::message::serializer::vec_to_protocol_json
        28,945 │     1.82% │ buttplug::util::async_manager::spawn
        25,678 │     1.61% │ buttplug::server::device::hardware::communication
        22,341 │     1.40% │ buttplug::core::message::ButtplugCurrentSpecServerMessage
```

### wasm-objdump 匯出函數：

```
Export[7]:
 - memory[0] -> "memory"
 - func[142] <buttplug_create_embedded_wasm_server> -> "buttplug_create_embedded_wasm_server"
 - func[143] <buttplug_free_embedded_wasm_server> -> "buttplug_free_embedded_wasm_server"
 - func[144] <buttplug_client_send_json_message> -> "buttplug_client_send_json_message"
 - func[145] <buttplug_activate_env_logger> -> "buttplug_activate_env_logger"
 - func[146] <__wbindgen_malloc> -> "__wbindgen_malloc"
 - func[147] <__wbindgen_free> -> "__wbindgen_free"
```

---

## ⚡ WASM 檔案大小優化

### 如果想減少 WASM 檔案大小：

#### 1. 啟用 LTO (Link Time Optimization)

```toml
# Cargo.toml
[profile.release]
lto = true              # 連結時間優化
opt-level = "z"         # 優化檔案大小
codegen-units = 1       # 單一編譯單元
panic = "abort"         # 減少 panic 處理代碼
strip = true            # 移除符號資訊
```

#### 2. 使用輕量級記憶體分配器

```toml
[dependencies]
wee_alloc = "0.4.5"
```

```rust
// 在 lib.rs 中
#[cfg(feature = "wee_alloc")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;
```

#### 3. 精確控制功能

```toml
[dependencies]
buttplug = { 
  version = "7.1.13", 
  default-features = false,  # 關閉預設功能
  features = ["wasm"],       # 只啟用需要的功能
}

# 其他依賴也可以類似處理
serde = { version = "1.0", default-features = false, features = ["derive"] }
tokio = { version = "1.0", default-features = false, features = ["sync", "macros"] }
```

#### 4. 建置時優化

```bash
# 使用最佳化建置
wasm-pack build --release --target web

# 進一步壓縮（可選）
wasm-opt -Oz -o buttplug_server_bg_optimized.wasm buttplug_server_bg.wasm
```

---

## 🎯 總結

### 🚨 分析 WASM 的黃金法則

```bash
# ✅ 正確的分析流程
wasm-pack build --dev --target web    # 必須使用 --dev 模式
wasm-objdump -d buttplug_server_bg.wasm    # 才能看到完整函數
```

### 包含的主要 Buttplug 功能：

1. **伺服器管理**
   - `ButtplugServer` 建立和管理
   - `ButtplugServerBuilder` 建構器

2. **訊息處理**
   - 訊息序列化/反序列化
   - JSON 協定處理
   - 訊息版本管理

3. **設備通訊**
   - 硬體抽象層介面
   - 藍牙通訊管理
   - 設備發現和連接

4. **異步運行時**
   - `async_manager` 任務調度
   - 事件流處理

5. **錯誤處理**
   - `ButtplugDeviceError` 和相關錯誤類型

### 不包含的功能：

- 非 WebAssembly 平台的功能
- 未使用的設備協定
- 除錯和測試專用功能
- `default-features = false` 排除的功能

### 🔧 工具安裝快速參考

| 工具 | 安裝指令 | 用途 |
|------|----------|------|
| **wasm-objdump** | `brew install wabt` (macOS)<br/>`sudo apt install wabt` (Ubuntu) | 反組譯 WASM |
| **twiggy** | `cargo install twiggy` | 分析程式碼大小 |
| **wasm2wat** | 包含在 WABT 中 | 轉換為文字格式 |

### ⚠️ 關鍵提醒

**記住**：
- 📊 **分析時**：使用 `wasm-pack build --dev`
- 🚀 **部署時**：使用 `wasm-pack build --release`
- 🔍 **找不到函數**：檢查是否用了 `--dev` 模式

**最終結果**：你的 `buttplug_server_bg.wasm` 檔案會是一個精簡但功能完整的 Buttplug 服務器實作，包含所有必要的核心功能來處理藍牙設備控制。但只有在使用 `--dev` 模式建置時，才能清楚看到所有函數的結構和組成！