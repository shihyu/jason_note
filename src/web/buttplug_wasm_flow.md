# Buttplug WASM 藍牙設備控制流程說明

## 概述

本文件說明 Buttplug WASM 庫如何透過 Web Bluetooth API 掃描、配對藍牙設備並控制按摩棒振動的完整流程。

## 主要組件和函數（附檔案名稱）

### 1. 初始化伺服器
**函數**: `buttplug_create_embedded_wasm_server` **(📁 lib.rs)**
- 建立 `ButtplugServer` 實例
- 設定 `WebBluetoothCommunicationManagerBuilder` **(📁 webbluetooth_manager.rs)**
- 設置事件流監聽器
- 回傳伺服器指標供後續使用

### 2. 藍牙掃描流程
**核心函數**: `WebBluetoothCommunicationManager::start_scanning` **(📁 webbluetooth_manager.rs)**

掃描流程：
1. 檢查瀏覽器是否支援 Web Bluetooth API
2. 從設備配置管理器獲取所有支援的藍牙設備規格
3. 建立掃描過濾器（根據設備名稱和服務UUID）
4. 呼叫 `navigator.bluetooth.requestDevice()` 彈出設備選擇對話框
5. 使用者選擇設備後，建立 `WebBluetoothHardwareConnector`
6. 發送 `DeviceFound` 事件

```rust
// 關鍵程式碼片段
let nav = web_sys::window().unwrap().navigator();
match JsFuture::from(nav.bluetooth().unwrap().request_device(&options)).await {
    Ok(device) => {
        let bt_device = BluetoothDevice::from(device);
        let device_creator = Box::new(WebBluetoothHardwareConnector::new(bt_device));
        sender_clone.send(HardwareCommunicationManagerEvent::DeviceFound {
            name, address, creator: device_creator,
        }).await;
    }
}
```

### 3. 設備連接和配置
**主要類別**: `WebBluetoothHardwareSpecializer` **(📁 webbluetooth_hardware.rs)**

連接流程：
1. `connect()` - 建立GATT連接
2. `specialize()` - 根據協定規格配置設備：
   - 連接到GATT伺服器
   - 枚舉所需的服務和特徵值
   - 設定斷線事件處理器
   - 建立 `WebBluetoothHardware` 實例

### 4. 設備控制
**核心函數**: `run_webbluetooth_loop` **(📁 webbluetooth_hardware.rs)**

這是設備控制的事件循環，處理以下指令：

#### 寫入指令（控制振動）
```rust
WebBluetoothDeviceCommand::Write(write_cmd, waker) => {
    let chr = char_map.get(&write_cmd.endpoint()).unwrap().clone();
    JsFuture::from(chr.write_value_with_u8_array(&mut write_cmd.data().clone())).await;
}
```

#### 讀取指令
```rust
WebBluetoothDeviceCommand::Read(read_cmd, waker) => {
    let read_value = JsFuture::from(chr.read_value()).await;
    // 處理讀取的資料
}
```

#### 訂閱通知
```rust
WebBluetoothDeviceCommand::Subscribe(subscribe_cmd, waker) => {
    // 設定特徵值變化回調
    chr.set_oncharacteristicvaluechanged(Some(onchange_callback));
    JsFuture::from(chr.start_notifications()).await;
}
```

### 5. 訊息處理
**函數**: `buttplug_client_send_json_message` **(📁 lib.rs)**
- 接收來自JavaScript的JSON訊息
- 反序列化為Buttplug協定訊息
- 透過伺服器處理訊息
- 回傳響應

## 主要流程圖

```mermaid
graph TD
    A["JavaScript 呼叫<br/>buttplug_create_embedded_wasm_server<br/>lib.rs"] --> B["建立 ButtplugServer<br/>設定 WebBluetoothCommunicationManagerBuilder<br/>webbluetooth_manager.rs"]
    
    B --> C["JavaScript 發送 StartScanning 訊息<br/>lib.rs: buttplug_client_send_json_message"]
    
    C --> D["WebBluetoothCommunicationManager::start_scanning<br/>webbluetooth_manager.rs"]
    
    D --> E["檢查瀏覽器 Web Bluetooth 支援"]
    E -->|支援| F["建立設備過濾器<br/>包含設備名稱和服務 UUID"]
    E -->|不支援| G["錯誤：不支援 WebBluetooth"]
    
    F --> H["呼叫 navigator.bluetooth.requestDevice<br/>彈出設備選擇對話框"]
    
    H --> I["使用者選擇藍牙設備"]
    I --> J["建立 WebBluetoothHardwareConnector<br/>webbluetooth_hardware.rs"]
    
    J --> K["發送 DeviceFound 事件"]
    K --> L["自動觸發設備連接<br/>WebBluetoothHardwareConnector::connect<br/>webbluetooth_hardware.rs"]
    
    L --> M["WebBluetoothHardwareSpecializer::specialize<br/>webbluetooth_hardware.rs"]
    
    M --> N["建立 GATT 連接<br/>device.gatt().connect()"]
    N --> O["枚舉服務和特徵值<br/>根據協定規格配置"]
    O --> P["設定斷線事件處理器"]
    P --> Q["啟動設備事件循環<br/>run_webbluetooth_loop<br/>webbluetooth_hardware.rs"]
    
    Q --> R["設備準備就緒<br/>等待控制指令"]
    
    R --> S["JavaScript 發送振動指令<br/>buttplug_client_send_json_message<br/>lib.rs"]
    
    S --> T["解析 JSON 訊息<br/>轉換為 Buttplug 協定"]
    T --> U["WebBluetoothDeviceCommand::Write<br/>webbluetooth_hardware.rs"]
    
    U --> V["透過藍牙特徵值寫入資料<br/>chr.write_value_with_u8_array"]
    V --> W["設備執行振動"]
    
    W --> X["設備回傳狀態<br/>透過 Notification 或 Read"]
    X --> Y["回傳響應給 JavaScript"]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style D fill:#e8f5e8
    style M fill:#fff3e0
    style Q fill:#fce4ec
    style S fill:#e1f5fe
```

## 詳細時序圖

```mermaid
sequenceDiagram
    participant JS as JavaScript
    participant LIB as lib.rs
    participant MGR as webbluetooth_manager.rs
    participant HW as webbluetooth_hardware.rs
    participant Browser as "瀏覽器 Web Bluetooth API"
    participant Device as "藍牙設備"

    Note over JS,Device: 1. 初始化階段
    JS->>LIB: buttplug_create_embedded_wasm_server(callback)
    LIB->>MGR: 建立 WebBluetoothCommunicationManagerBuilder
    LIB->>LIB: 建立 ButtplugServer
    LIB-->>JS: 回傳伺服器指標

    Note over JS,Device: 2. 掃描和連接階段
    JS->>LIB: buttplug_client_send_json_message("StartScanning")
    LIB->>MGR: start_scanning()
    MGR->>Browser: navigator.bluetooth.requestDevice()
    Browser->>JS: 彈出設備選擇對話框
    JS->>Browser: 使用者選擇設備
    Browser-->>MGR: 回傳選中的設備
    MGR->>HW: 建立 WebBluetoothHardwareConnector
    MGR-->>LIB: DeviceFound 事件

    Note over JS,Device: 3. 設備配置階段
    LIB->>HW: connect()
    HW->>HW: specialize()
    HW->>Browser: device.gatt().connect()
    Browser->>Device: 建立 GATT 連接
    Device-->>Browser: 連接成功
    Browser-->>HW: GATT 伺服器連接
    HW->>Browser: 枚舉服務和特徵值
    Browser->>Device: 查詢服務
    Device-->>Browser: 回傳服務資訊
    Browser-->>HW: 服務和特徵值資訊
    HW->>HW: 啟動 run_webbluetooth_loop
    HW-->>LIB: 設備準備就緒
    LIB-->>JS: 設備連接完成

    Note over JS,Device: 4. 控制階段
    JS->>LIB: buttplug_client_send_json_message("VibrateCmd")
    LIB->>HW: WebBluetoothDeviceCommand::Write
    HW->>Browser: chr.write_value_with_u8_array()
    Browser->>Device: 藍牙資料傳輸
    Device->>Device: 執行振動
    Device-->>Browser: 確認執行
    Browser-->>HW: 寫入完成
    HW-->>LIB: 指令執行成功
    LIB-->>JS: 回傳響應

    Note over JS,Device: 5. 持續監控
    Device->>Browser: 狀態更新 (若有訂閱)
    Browser->>HW: oncharacteristicvaluechanged
    HW->>LIB: HardwareEvent::Notification
    LIB->>JS: 回調通知
```

## 關鍵檔案功能說明

| 檔案 | 主要功能 |
|------|----------|
| **📁 lib.rs** | WASM 介面層，處理 JavaScript 與 Rust 之間的通訊 |
| **📁 webbluetooth_manager.rs** | 藍牙設備管理器，負責掃描和發現設備 |
| **📁 webbluetooth_hardware.rs** | 藍牙硬體抽象層，負責設備連接和控制 |
| **📁 mod.rs** | 模組定義檔案，匯出公共介面 |

## 振動控制範例

當你想控制設備振動時，會發送類似這樣的JSON訊息：

```json
{
  "VibrateCmd": {
    "Id": 1,
    "DeviceIndex": 0,
    "Speeds": [{"Index": 0, "Speed": 0.5}]
  }
}
```

這個訊息最終會轉換為藍牙寫入指令，透過 `WebBluetoothDeviceCommand::Write` 發送到設備的相應特徵值。

## 技術特點

- **異步架構**: 使用 Tokio 的 mpsc 通道在不同組件間傳遞訊息和事件
- **Web Standards**: 基於 Web Bluetooth API 標準
- **類型安全**: 透過 Rust 的類型系統確保記憶體安全
- **跨平台**: 支援所有相容 Web Bluetooth 的瀏覽器

## 錯誤處理

系統包含多層錯誤處理：
1. **瀏覽器支援檢查**: 確認 Web Bluetooth API 可用性
2. **設備連接錯誤**: 處理 GATT 連接失敗
3. **通訊錯誤**: 處理藍牙讀寫操作失敗
4. **協定錯誤**: 處理訊息序列化/反序列化錯誤

整個系統設計允許 JavaScript 應用程式透過 WASM 介面安全且高效地控制藍牙按摩棒設備。