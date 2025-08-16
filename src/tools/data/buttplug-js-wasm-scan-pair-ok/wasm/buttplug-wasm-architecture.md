# Buttplug WASM 配對振動功能分析

## 概述

**是的，配對振動功能確實會調用 pkg 的 wasm 執行檔。**

本專案透過 WebAssembly (WASM) 將 Rust 實作的 Buttplug 協議整合到 JavaScript 環境中，實現設備配對和振動控制功能。

## 核心架構

```
JavaScript 前端 → TypeScript 連接器 → WASM 綁定 → Rust 核心 → 設備通訊
```

## WASM 模組載入流程

### 1. 模組載入 (src/index.ts:19-22)
```typescript
const wasmModule = await import('../rust/pkg/buttplug_wasm.js');
// 對於 web 目標，需要手動初始化 WASM
// 使用公共路徑中的 WASM 檔案
await wasmModule.default('/wasm/buttplug_wasm_bg.wasm');
ButtplugWasmClientConnector.wasmInstance = wasmModule;
```

### 2. 伺服器創建 (src/index.ts:42-44)
```typescript
this.client = ButtplugWasmClientConnector.wasmInstance.buttplug_create_embedded_wasm_server((msgs) => {
  this.emitMessage(msgs);
}, this.serverPtr);
```

### 3. 訊息傳送 (src/index.ts:51-53)
```typescript
ButtplugWasmClientConnector.wasmInstance.buttplug_client_send_json_message(
  this.client, 
  new TextEncoder().encode('[' + msg.toJSON() + ']'), 
  (output) => {
    this.emitMessage(output);
  }
);
```

## 關鍵 WASM 函數

在 `rust/pkg/buttplug_wasm.js` 中暴露的核心函數：

| 函數名稱 | 功能描述 |
|---------|---------|
| `buttplug_create_embedded_wasm_server()` | 創建嵌入式 Buttplug 伺服器 |
| `buttplug_client_send_json_message()` | 發送 JSON 訊息到 WASM |
| `buttplug_activate_env_logger()` | 激活日誌記錄系統 |
| `buttplug_free_embedded_wasm_server()` | 釋放伺服器資源 |

## Rust 核心實作

### WebBluetooth 管理器 (webbluetooth_manager.rs)
```rust
impl HardwareCommunicationManager for WebBluetoothCommunicationManager {
  fn start_scanning(&mut self) -> ButtplugResultFuture {
    // 透過 WebBluetooth API 掃描設備
    // 建立設備過濾器和服務列表
    // 創建 WebBluetoothHardwareConnector
  }
}
```

### WASM 綁定函數 (lib.rs:53-70)
```rust
#[wasm_bindgen]
pub fn buttplug_create_embedded_wasm_server(
  callback: &FFICallback,
) -> *mut ButtplugWASMServer {
  let mut builder = ButtplugServerBuilder::default();
  builder.comm_manager(WebBluetoothCommunicationManagerBuilder::default());
  let server = Arc::new(builder.finish().unwrap());
  // ... 事件流處理
}
```

## 配對與振動流程

### 1. 設備掃描階段
```javascript
// example/index.js:103
await globalClient.startScanning();
```

### 2. 設備配對階段
```javascript
// example/index.js:107-111
globalClient.addListener('deviceadded', (device) => {
  addLog(`找到設備: ${device.name || 'Unknown'} (${device.index})`);
  connectedDevices.push(device);
  updateDeviceList();
});
```

### 3. 振動控制階段
```javascript
// example/index.js:181-187
for (const device of connectedDevices) {
  if (device.vibrateAttributes && device.vibrateAttributes.length > 0) {
    const vibrateArray = new Array(device.vibrateAttributes.length).fill(intensity);
    await device.vibrate(vibrateArray);
    addLog(`設備 ${device.name} 開始振動，強度: ${Math.round(intensity * 100)}%`);
  }
}
```

## 檔案結構

```
wasm/
├── src/
│   └── index.ts                    # TypeScript 連接器
├── rust/
│   ├── src/
│   │   ├── lib.rs                  # WASM 綁定主檔案
│   │   └── webbluetooth/           # WebBluetooth 實作
│   │       ├── mod.rs
│   │       ├── webbluetooth_manager.rs
│   │       └── webbluetooth_hardware.rs
│   └── pkg/                        # 編譯輸出
│       ├── buttplug_wasm.js        # JavaScript 綁定
│       ├── buttplug_wasm_bg.wasm   # WASM 二進位檔案
│       └── buttplug_wasm.d.ts      # TypeScript 型別定義
└── example/
    ├── index.html                  # 測試頁面
    └── index.js                    # 前端測試程式
```

## 詳細調用流程

### 初始化階段
1. 頁面載入時載入 WASM 模組
2. 創建 `ButtplugWasmClientConnector` 實例
3. 透過 `buttplug_create_embedded_wasm_server()` 創建 WASM 伺服器

### 掃描配對階段
1. 前端調用 `globalClient.startScanning()`
2. TypeScript 連接器透過 `send()` 方法發送掃描請求
3. `buttplug_client_send_json_message()` 將訊息傳送到 WASM
4. Rust 核心的 `WebBluetoothCommunicationManager` 處理掃描邏輯
5. 透過 WebBluetooth API 與瀏覽器互動
6. 找到設備時觸發 `deviceadded` 事件

### 振動控制階段
1. 前端調用 `device.vibrate(vibrateArray)`
2. 振動指令透過相同的訊息傳遞機制送到 WASM
3. Rust 核心處理振動協議
4. 透過 WebBluetooth 發送振動指令到實際硬體

## 關鍵觀察

1. **所有設備操作都經過 WASM**：無論是掃描、配對還是振動控制，都必須透過 `buttplug_wasm_bg.wasm` 執行檔處理
2. **非同步訊息機制**：使用回調函數處理 WASM 與 JavaScript 之間的非同步通訊
3. **WebBluetooth 整合**：Rust 代碼直接與瀏覽器的 WebBluetooth API 整合
4. **記憶體管理**：透過 `buttplug_free_embedded_wasm_server()` 確保適當的資源釋放

## 總結

所有的配對和振動功能都透過以下路徑執行：

1. **JavaScript 前端** 呼叫 Buttplug Client API
2. **TypeScript 連接器** 將請求轉換為 WASM 調用
3. **WASM 綁定層** 調用 `buttplug_wasm_bg.wasm` 執行檔
4. **Rust 核心** 處理 Buttplug 協議和設備通訊
5. **WebBluetooth API** 實際與硬體設備互動

因此，**所有的配對振動功能都依賴於 pkg 目錄下的 WASM 執行檔**。
