# Buttplug 函數呼叫詳細整理

## 📁 lib.rs - 主要 WASM 介面檔案

### 匯入的 Buttplug 模組
```rust
use buttplug::{
  core::message::{ButtplugCurrentSpecServerMessage, serializer::vec_to_protocol_json},
  server::ButtplugServer,
  util::async_manager, 
  server::ButtplugServerBuilder, 
  core::message::{
    BUTTPLUG_CURRENT_MESSAGE_SPEC_VERSION, 
    serializer::{ButtplugSerializedMessage, ButtplugMessageSerializer, ButtplugServerJSONSerializer}
  }
};
```

### 函數呼叫詳情

#### 1. `send_server_message` 函數
```rust
pub fn send_server_message(
  message: &ButtplugCurrentSpecServerMessage,  // ← Buttplug 類型
  callback: &FFICallback,
) {
  let msg_array = [message.clone()];
  let json_msg = vec_to_protocol_json(&msg_array);  // ← Buttplug 函數呼叫
  // ...
}
```
**呼叫的 Buttplug 函數**：
- `vec_to_protocol_json()` - 將訊息陣列轉換為 JSON

#### 2. `buttplug_create_embedded_wasm_server` 函數
```rust
pub fn buttplug_create_embedded_wasm_server(
  callback: &FFICallback,
) -> *mut ButtplugWASMServer {
  let mut builder = ButtplugServerBuilder::default();  // ← Buttplug 函數呼叫
  builder.comm_manager(WebBluetoothCommunicationManagerBuilder::default());  // ← Buttplug 函數呼叫
  let server = Arc::new(builder.finish().unwrap());  // ← Buttplug 函數呼叫
  let event_stream = server.event_stream();  // ← Buttplug 函數呼叫
  // ...
  async_manager::spawn(async move {  // ← Buttplug 函數呼叫
    // ...
    while let Some(message) = event_stream.next().await {
      send_server_message(&ButtplugCurrentSpecServerMessage::try_from(message).unwrap(), &callback);  // ← Buttplug 函數呼叫
    }
  });
}
```
**呼叫的 Buttplug 函數**：
- `ButtplugServerBuilder::default()` - 建立伺服器建構器
- `builder.comm_manager()` - 設定通訊管理器
- `builder.finish()` - 完成伺服器建構
- `server.event_stream()` - 獲取事件流
- `async_manager::spawn()` - 異步任務派發
- `ButtplugCurrentSpecServerMessage::try_from()` - 訊息類型轉換

#### 3. `buttplug_client_send_json_message` 函數
```rust
pub fn buttplug_client_send_json_message(
  server_ptr: *mut ButtplugWASMServer,
  buf: &[u8],
  callback: &FFICallback,
) {
  let serializer = ButtplugServerJSONSerializer::default();  // ← Buttplug 函數呼叫
  serializer.force_message_version(&BUTTPLUG_CURRENT_MESSAGE_SPEC_VERSION);  // ← Buttplug 函數呼叫
  let input_msg = serializer.deserialize(&ButtplugSerializedMessage::Text(std::str::from_utf8(buf).unwrap().to_owned())).unwrap();  // ← Buttplug 函數呼叫
  async_manager::spawn(async move {  // ← Buttplug 函數呼叫
    let response = server.parse_message(input_msg[0].clone()).await.unwrap();  // ← Buttplug 函數呼叫
    send_server_message(&response.try_into().unwrap(), &callback);
  });
}
```
**呼叫的 Buttplug 函數**：
- `ButtplugServerJSONSerializer::default()` - 建立 JSON 序列化器
- `serializer.force_message_version()` - 強制訊息版本
- `serializer.deserialize()` - 反序列化訊息
- `ButtplugSerializedMessage::Text()` - 建立文字訊息
- `async_manager::spawn()` - 異步任務派發
- `server.parse_message()` - 解析並處理訊息

---

## 📁 webbluetooth_manager.rs - 藍牙管理器檔案

### 匯入的 Buttplug 模組
```rust
use buttplug::{
  core::ButtplugResultFuture,
  server::device::{
    configuration::ProtocolCommunicationSpecifier,
    hardware::communication::{
      HardwareCommunicationManager, 
      HardwareCommunicationManagerBuilder,
      HardwareCommunicationManagerEvent,
    },
  },
  util::device_configuration::create_test_dcm,
};
```

### 函數呼叫詳情

#### 1. `WebBluetoothCommunicationManagerBuilder` 實作
```rust
impl HardwareCommunicationManagerBuilder for WebBluetoothCommunicationManagerBuilder {  // ← 實作 Buttplug trait
  fn finish(&mut self, sender: Sender<HardwareCommunicationManagerEvent>) -> Box<dyn HardwareCommunicationManager> {  // ← Buttplug 類型
    Box::new(WebBluetoothCommunicationManager {
      sender,
    })
  }
}
```
**實作的 Buttplug trait**：
- `HardwareCommunicationManagerBuilder` - 硬體通訊管理器建構器

#### 2. `WebBluetoothCommunicationManager` 實作
```rust
impl HardwareCommunicationManager for WebBluetoothCommunicationManager {  // ← 實作 Buttplug trait
  fn name(&self) -> &'static str { /* ... */ }
  fn can_scan(&self) -> bool { /* ... */ }
  fn start_scanning(&mut self) -> ButtplugResultFuture { /* ... */ }  // ← Buttplug 類型
  fn stop_scanning(&mut self) -> ButtplugResultFuture { /* ... */ }  // ← Buttplug 類型
}
```

#### 3. `start_scanning` 函數內的呼叫
```rust
fn start_scanning(&mut self) -> ButtplugResultFuture {
  // ...
  let config_manager = create_test_dcm(false);  // ← Buttplug 函數呼叫
  // ...
  for vals in config_manager.protocol_device_configurations().iter() {  // ← Buttplug 函數呼叫
    for config in vals.1 {
      if let ProtocolCommunicationSpecifier::BluetoothLE(btle) = &config {  // ← Buttplug 類型匹配
        for name in btle.names() {  // ← Buttplug 函數呼叫
          // ...
        }
        for (service, _) in btle.services() {  // ← Buttplug 函數呼叫
          // ...
        }
      }
    }
  }
  // ...
  if sender_clone.send(HardwareCommunicationManagerEvent::DeviceFound {  // ← Buttplug 事件類型
    name,
    address,
    creator: device_creator,
  }).await.is_err() {
    // ...
  }
  let _ = sender_clone.send(HardwareCommunicationManagerEvent::ScanningFinished).await;  // ← Buttplug 事件類型
}
```
**呼叫的 Buttplug 函數**：
- `create_test_dcm()` - 建立測試設備配置管理器
- `config_manager.protocol_device_configurations()` - 獲取協定設備配置
- `btle.names()` - 獲取設備名稱
- `btle.services()` - 獲取藍牙服務
- `HardwareCommunicationManagerEvent::DeviceFound` - 設備發現事件
- `HardwareCommunicationManagerEvent::ScanningFinished` - 掃描完成事件

---

## 📁 webbluetooth_hardware.rs - 藍牙硬體檔案

### 匯入的 Buttplug 模組
```rust
use buttplug::{
  core::{
    errors::ButtplugDeviceError,
    message::Endpoint,
  },
  server::device::{
    configuration::{BluetoothLESpecifier, ProtocolCommunicationSpecifier},
    hardware::{
      Hardware,
      HardwareConnector,
      HardwareEvent,
      HardwareInternal,
      HardwareReadCmd,
      HardwareReading,
      HardwareSpecializer,
      HardwareSubscribeCmd,
      HardwareUnsubscribeCmd,
      HardwareWriteCmd,
    },
  },
  util::future::{ButtplugFuture, ButtplugFutureStateShared},
};
```

### 函數呼叫詳情

#### 1. `WebBluetoothHardwareConnector` 實作
```rust
impl HardwareConnector for WebBluetoothHardwareConnector {  // ← 實作 Buttplug trait
  fn specifier(&self) -> ProtocolCommunicationSpecifier {  // ← Buttplug 類型
    ProtocolCommunicationSpecifier::BluetoothLE(BluetoothLESpecifier::new_from_device(  // ← Buttplug 函數呼叫
      &self.device.as_ref().unwrap().device.name().unwrap(),
      &HashMap::new(),
      &[]
    ))    
  }

  async fn connect(&mut self) -> Result<Box<dyn HardwareSpecializer>, ButtplugDeviceError> {  // ← Buttplug 類型
    Ok(Box::new(WebBluetoothHardwareSpecializer::new(self.device.take().unwrap())))
  }
}
```
**呼叫的 Buttplug 函數**：
- `BluetoothLESpecifier::new_from_device()` - 從設備建立藍牙規格
- `ProtocolCommunicationSpecifier::BluetoothLE()` - 藍牙 LE 協定規格

#### 2. `WebBluetoothHardwareSpecializer` 實作
```rust
impl HardwareSpecializer for WebBluetoothHardwareSpecializer {  // ← 實作 Buttplug trait
  async fn specialize(
    &mut self,
    specifiers: &[ProtocolCommunicationSpecifier],  // ← Buttplug 類型
  ) -> Result<Hardware, ButtplugDeviceError> {  // ← Buttplug 類型
    // ...
    let device_impl: Box<dyn HardwareInternal> = Box::new(WebBluetoothHardware::new(  // ← Buttplug trait
      event_sender,
      receiver,
      command_sender,
    ));
    Ok(Hardware::new(&name, &address, &[], device_impl))  // ← Buttplug 函數呼叫
  }
}
```
**呼叫的 Buttplug 函數**：
- `Hardware::new()` - 建立硬體實例

#### 3. `WebBluetoothHardware` 實作
```rust
impl HardwareInternal for WebBluetoothHardware {  // ← 實作 Buttplug trait
  fn event_stream(&self) -> broadcast::Receiver<HardwareEvent> {  // ← Buttplug 類型
    self.event_sender.subscribe()
  }

  fn disconnect(&self) -> BoxFuture<'static, Result<(), ButtplugDeviceError>> {  // ← Buttplug 類型
    // ...
  }

  fn read_value(
    &self,
    msg: &HardwareReadCmd,  // ← Buttplug 類型
  ) -> BoxFuture<'static, Result<HardwareReading, ButtplugDeviceError>> {  // ← Buttplug 類型
    // ...
    Box::pin(async move {
      let fut = WebBluetoothReadResultFuture::default();
      let waker = fut.get_state_clone();  // ← Buttplug 函數呼叫
      sender.send(WebBluetoothDeviceCommand::Read(msg, waker)).await;
      fut.await
    })
  }

  fn write_value(&self, msg: &HardwareWriteCmd) -> BoxFuture<'static, Result<(), ButtplugDeviceError>> {  // ← Buttplug 類型
    // ...
  }

  fn subscribe(&self, msg: &HardwareSubscribeCmd) -> BoxFuture<'static, Result<(), ButtplugDeviceError>> {  // ← Buttplug 類型
    // ...
  }

  fn unsubscribe(&self, _msg: &HardwareUnsubscribeCmd) -> BoxFuture<'static, Result<(), ButtplugDeviceError>> {  // ← Buttplug 類型
    // ...
  }
}
```

#### 4. `run_webbluetooth_loop` 函數內的呼叫
```rust
async fn run_webbluetooth_loop(
  device: BluetoothDevice,
  btle_protocol: BluetoothLESpecifier,  // ← Buttplug 類型
  device_local_event_sender: mpsc::Sender<WebBluetoothEvent>,
  device_external_event_sender: broadcast::Sender<HardwareEvent>,  // ← Buttplug 類型
  mut device_command_receiver: mpsc::Receiver<WebBluetoothDeviceCommand>,
) {
  // ...
  for (service_uuid, service_endpoints) in btle_protocol.services() {  // ← Buttplug 函數呼叫
    // ...
  }
  // ...
  event_sender.send(HardwareEvent::Disconnected(id.clone())).unwrap();  // ← Buttplug 事件
  // ...
  let reading = HardwareReading::new(read_cmd.endpoint(), &body);  // ← Buttplug 函數呼叫
  // ...
  event_sender.send(HardwareEvent::Notification(id.clone(), ep, value_vec)).unwrap();  // ← Buttplug 事件
}
```
**呼叫的 Buttplug 函數**：
- `btle_protocol.services()` - 獲取藍牙服務
- `HardwareEvent::Disconnected()` - 斷線事件
- `HardwareReading::new()` - 建立讀取結果
- `HardwareEvent::Notification()` - 通知事件

---

## 📁 mod.rs - 模組匯出檔案

### 匯出內容
```rust
mod webbluetooth_hardware;
mod webbluetooth_manager;

pub use webbluetooth_hardware::{WebBluetoothHardwareConnector, WebBluetoothHardware};
pub use webbluetooth_manager::{WebBluetoothCommunicationManagerBuilder,WebBluetoothCommunicationManager};
```

**說明**：此檔案只是模組匯出，沒有直接呼叫 Buttplug 函數。

---

## 總結表格

| 檔案 | 主要 Buttplug 函數呼叫 | 實作的 Buttplug Trait |
|------|----------------------|---------------------|
| **lib.rs** | `vec_to_protocol_json()`, `ButtplugServerBuilder::default()`, `server.event_stream()`, `async_manager::spawn()`, `ButtplugServerJSONSerializer::default()` | 無 |
| **webbluetooth_manager.rs** | `create_test_dcm()`, `config_manager.protocol_device_configurations()`, `btle.names()`, `btle.services()` | `HardwareCommunicationManager`, `HardwareCommunicationManagerBuilder` |
| **webbluetooth_hardware.rs** | `BluetoothLESpecifier::new_from_device()`, `Hardware::new()`, `HardwareReading::new()`, `fut.get_state_clone()` | `HardwareConnector`, `HardwareSpecializer`, `HardwareInternal` |
| **mod.rs** | 無 | 無 |

## 類型別呼叫統計

### 伺服器管理 (4次)
- `ButtplugServerBuilder::default()`
- `builder.comm_manager()`
- `builder.finish()`
- `server.event_stream()`

### 訊息處理 (6次)
- `vec_to_protocol_json()`
- `ButtplugServerJSONSerializer::default()`
- `serializer.force_message_version()`
- `serializer.deserialize()`
- `server.parse_message()`
- `ButtplugCurrentSpecServerMessage::try_from()`

### 硬體管理 (8次)
- `create_test_dcm()`
- `config_manager.protocol_device_configurations()`
- `btle.names()`
- `btle.services()`
- `BluetoothLESpecifier::new_from_device()`
- `Hardware::new()`
- `HardwareReading::new()`
- `fut.get_state_clone()`

### 事件處理 (3次)
- `HardwareEvent::Disconnected()`
- `HardwareEvent::Notification()`
- `HardwareCommunicationManagerEvent::DeviceFound`

### 異步管理 (2次)
- `async_manager::spawn()` (呼叫2次)

**總計：23個 Buttplug 函數呼叫**