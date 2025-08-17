# Rust Crate 依賴與 API 設計完整指南

## 🤔 問題背景

你有一個 `buttplug_server` crate，裡面依賴了 `buttplug_server_device_config`：

```toml
[dependencies]
buttplug_server_device_config = { path = "../buttplug_server_device_config" }
```

現在要編譯成 `.so` 文件給外部程序使用，**關鍵問題是**：
> 外部程序能不能透過 `buttplug_server` 直接使用 `buttplug_server_device_config` 的功能？

## 📝 核心概念

### 重要觀念 1：Cargo.toml 依賴 ≠ 公開 API
```rust
// ❌ 這樣寫，外部看不到 buttplug_server_device_config
// Cargo.toml 有依賴，但沒有 pub use

// ✅ 要這樣寫才能讓外部使用
pub use buttplug_server_device_config::*;
```

**白話解釋**：
想像你家有一個工具箱（`buttplug_server`），裡面放了一把螺絲起子（`buttplug_server_device_config`）。

- 📦 **Cargo.toml 的依賴** = 你把螺絲起子放進工具箱裡
- 🚪 **pub use** = 你在工具箱外面貼標籤說"裡面有螺絲起子，可以直接拿"

**沒有 pub use 的情況**：
```rust
// 你的 lib.rs 裡面
use buttplug_server_device_config::DeviceConfig;  // 只有你自己能用

// 外部想用：
use buttplug_server::DeviceConfig;  // ❌ 找不到！編譯錯誤
```
就像朋友想借螺絲起子，但你沒貼標籤，他不知道工具箱裡有什麼。

**有 pub use 的情況**：
```rust
// 你的 lib.rs 裡面  
pub use buttplug_server_device_config::DeviceConfig;  // 重新導出

// 外部可以用：
use buttplug_server::DeviceConfig;  // ✅ 可以找到！
```
你在工具箱外面貼了標籤，朋友就能直接跟你借螺絲起子。

### 重要觀念 2：Rust 模組預設私有
```rust
mod internal_stuff;        // ❌ 外部看不到
pub mod public_stuff;      // ✅ 外部可以看到
```

## 🎯 三種設計模式詳解

### 模式一：🏢 Facade 模式（統一門面）

**作法**：在 `buttplug_server/src/lib.rs` 裡重新導出

```rust
// === buttplug_server/src/lib.rs ===
// 重新導出子 crate 的功能
pub use buttplug_server_device_config::{
    DeviceConfig, 
    ConfigError, 
    load_config,
    // 你想要公開的所有東西
};

// 可以包裝一層更友善的 API
pub fn easy_load_device_config(path: &str) -> Result<DeviceConfig, ConfigError> {
    buttplug_server_device_config::load_config(path)
}

// 其他 server 功能
pub struct ButtplugServer { /* ... */ }
impl ButtplugServer {
    pub fn new() -> Self { /* ... */ }
}
```

**外部使用**：
```rust
// 外部 Cargo.toml 只需要一個依賴
[dependencies]
buttplug_server = { path = "../buttplug_server" }

// 使用時很簡潔
use buttplug_server::{ButtplugServer, DeviceConfig, easy_load_device_config};

fn main() {
    let config = easy_load_device_config("devices.json").unwrap();
    let server = ButtplugServer::new();
    // ...
}
```

**優點**：
- 🎯 一站式服務，外部只要依賴一個 crate
- 📦 API 統一，容易使用
- 🔧 可以包裝更友善的接口

**缺點**：
- 💥 內部架構改變會破壞外部 API
- 🔗 強耦合，子 crate 換名字就炸了
- 📈 維護成本高

---

### 模式二：🔒 Internal Only（各自獨立）

**作法**：`buttplug_server` 只管自己的事，不重新導出

```rust
// === buttplug_server/src/lib.rs ===
use buttplug_server_device_config::DeviceConfig; // 內部使用，不公開

pub struct ButtplugServer {
    config: DeviceConfig, // 內部使用
}

impl ButtplugServer {
    pub fn new_with_config_file(config_path: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let config = buttplug_server_device_config::load_config(config_path)?;
        Ok(Self { config })
    }
    
    // 只提供必要的 server 功能
    pub fn start(&self) { /* ... */ }
    pub fn stop(&self) { /* ... */ }
}
```

**外部使用**：
```rust
// 外部 Cargo.toml 需要兩個依賴
[dependencies]
buttplug_server = { path = "../buttplug_server" }
buttplug_server_device_config = { path = "../buttplug_server_device_config" }

// 使用時分開處理
use buttplug_server::ButtplugServer;
use buttplug_server_device_config::{DeviceConfig, load_config};

fn main() {
    // 方案 1：分開處理
    let config = load_config("devices.json").unwrap();
    let server = ButtplugServer::new_with_config_file("devices.json").unwrap();
    
    // 方案 2：或者直接用 server 包裝好的方法
    let server = ButtplugServer::new_with_config_file("devices.json").unwrap();
}
```

**優點**：
- 🛡️ API 穩定，內部改動不影響外部
- 🎨 各 crate 職責清楚
- 🔄 容易重構和測試

**缺點**：
- 📦 外部要記住多個依賴
- 📚 學習成本稍高

---

### 模式三：🌍 FFI/.so 模式（跨語言）

**作法**：提供 C 風格的 API

```rust
// === buttplug_server/src/lib.rs ===
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

// 內部 Rust 功能
use buttplug_server_device_config::load_config;

// 對外的 C API
#[no_mangle]
pub extern "C" fn buttplug_load_device_config(path: *const c_char) -> i32 {
    let c_str = unsafe { CStr::from_ptr(path) };
    let path_str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return -1, // 錯誤碼
    };
    
    match load_config(path_str) {
        Ok(_) => 0,  // 成功
        Err(_) => -1, // 失敗
    }
}

#[no_mangle]
pub extern "C" fn buttplug_server_start() -> i32 {
    // 啟動 server 邏輯
    0
}

#[no_mangle]
pub extern "C" fn buttplug_server_stop() -> i32 {
    // 停止 server 邏輯
    0
}

// 記憶體清理
#[no_mangle]
pub extern "C" fn buttplug_free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe { drop(CString::from_raw(ptr)) };
    }
}
```

**編譯設定**：
```toml
[lib]
name = "buttplug_server"
crate-type = ["cdylib", "rlib"]  # cdylib 生成 .so
```

**外部使用（C/C++）**：
```c
// buttplug.h
extern int buttplug_load_device_config(const char* path);
extern int buttplug_server_start();
extern int buttplug_server_stop();
extern void buttplug_free_string(char* ptr);

// main.c
#include "buttplug.h"

int main() {
    if (buttplug_load_device_config("devices.json") != 0) {
        printf("載入設定失敗\n");
        return 1;
    }
    
    if (buttplug_server_start() == 0) {
        printf("伺服器啟動成功\n");
    }
    
    buttplug_server_stop();
    return 0;
}
```

**外部使用（Python）**：
```python
import ctypes

# 載入 .so 檔
lib = ctypes.CDLL('./libbuttplug_server.so')

# 定義函數簽名
lib.buttplug_load_device_config.argtypes = [ctypes.c_char_p]
lib.buttplug_load_device_config.restype = ctypes.c_int

# 使用
result = lib.buttplug_load_device_config(b"devices.json")
if result == 0:
    print("載入成功")
else:
    print("載入失敗")
```

**優點**：
- 🌍 跨語言支援（C/C++/Python/Dart/Flutter）
- 🛡️ 完全隔離內部實作
- 📦 外部只需要 .so 檔案

**缺點**：
- 🔧 只能用你定義的 API，彈性低
- 💻 需要處理 C 字串和記憶體管理
- 🐛 錯誤處理比較麻煩

---

## 📊 模式比較表

| 特性 | Facade 模式 | Internal Only | FFI/.so 模式 |
|------|-------------|---------------|--------------|
| **外部依賴** | 只需 `buttplug_server` | 需要 `buttplug_server` + `buttplug_server_device_config` | 只需 `.so` 檔案 |
| **使用方式** | `use buttplug_server::DeviceConfig;` | `use buttplug_server_device_config::DeviceConfig;` | `buttplug_load_device_config("...")` |
| **API 穩定性** | ⚠️ 風險高 | ✅ 穩定 | ✅ 與內部無關 |
| **學習成本** | 🟢 簡單 | 🟡 中等 | 🔴 需要了解 FFI |
| **跨語言** | ❌ 只支援 Rust | ❌ 只支援 Rust | ✅ 支援所有語言 |
| **錯誤處理** | ✅ Rust Result | ✅ Rust Result | 🔴 錯誤碼 |
| **型別安全** | ✅ 完全安全 | ✅ 完全安全 | ⚠️ 需要小心 |

---

## 🎯 實際建議

### 針對 `buttplug_server` 專案：

1. **如果主要給 Rust 開發者用**：
   - 建議用 **Internal Only**，保持各 crate 獨立
   - 在 `buttplug_server` 提供高階 API，但不重新導出所有子 crate

2. **如果要跨語言支援**：
   - 用 **FFI 模式**，提供簡潔的 C API
   - 內部可以隨意重構，不影響外部

3. **如果想要最好用**：
   - 可以 **混合使用**：
     - Rust 用戶：提供 Internal Only + 一些便利的 Facade API
     - 其他語言：提供 FFI API

### 推薦的混合架構：

```rust
// === buttplug_server/src/lib.rs ===

// 1. 內部使用，不公開
use buttplug_server_device_config::{DeviceConfig, load_config};

// 2. 核心 server 功能
pub struct ButtplugServer { /* ... */ }

// 3. 便利的 Rust API（可選的 Facade）
pub mod config {
    pub use buttplug_server_device_config::{DeviceConfig, ConfigError};
    
    pub fn load_device_config(path: &str) -> Result<DeviceConfig, ConfigError> {
        buttplug_server_device_config::load_config(path)
    }
}

// 4. FFI API
#[no_mangle]
pub extern "C" fn buttplug_load_device_config(path: *const c_char) -> i32 {
    // ...
}
```

**外部使用**：
```rust
// Rust 用戶可以選擇
use buttplug_server::ButtplugServer;                    // 只用 server
use buttplug_server::config::load_device_config;       // 用便利 API
use buttplug_server_device_config::load_config;        // 直接用原始 crate
```

這樣既保持了彈性，也提供了便利性！

---

## 💡 總結

- **依賴寫在 Cargo.toml ≠ 外部可以用**
- **要用 `pub use` 才能重新導出**（就像在門口貼告示牌）
- **選擇模式要看使用場景**：
  - 給 Rust 用 → Internal Only
  - 要跨語言 → FFI 模式  
  - 要最方便 → 混合使用

記住：**API 設計是給人用的，不是給編譯器用的** 🚀