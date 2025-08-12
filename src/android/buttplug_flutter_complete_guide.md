# Flutter Buttplug 完整開發指南

## 目錄
1. [Buttplug 架構概述](#buttplug-架構概述)
2. [Intiface Central vs Buttplug Core](#intiface-central-vs-buttplug-core)
3. [Flutter 整合方案](#flutter-整合方案)
4. [硬體支援情況](#硬體支援情況)
5. [各家產品 BT 命令位置](#各家產品-bt-命令位置)
6. [APK/IPA 打包說明](#apkipa-打包說明)
7. [平台特定注意事項](#平台特定注意事項)
8. [實作範例](#實作範例)
9. [最佳實踐建議](#最佳實踐建議)

---

## Buttplug 架構概述

Buttplug 是一個開源的親密硬體控制標準和軟體專案，支援性玩具、按摩設備等硬體控制。

### 核心組件

```
┌─────────────────────────────────────────┐
│            應用程式層 (您的 Flutter App)     │
├─────────────────────────────────────────┤
│            Buttplug 客戶端              │
├─────────────────────────────────────────┤
│            Buttplug 服務器              │ 
├─────────────────────────────────────────┤
│            硬體通訊層                   │
└─────────────────────────────────────────┘
```

### 技術特色

- **實作語言**: Rust 核心，提供 C#、JS、Dart 等綁定
- **支援品牌**: Lovense、Kiiroo、The Handy、WeVibe、OSR-2/SR-6 等
- **連接方式**: Bluetooth LE、USB、HID、Serial
- **跨平台**: Desktop、Mobile、Web
- **開源協議**: BSD 3-Clause

---

## Intiface Central vs Buttplug Core

### 專案關係

| 專案 | 類型 | 功能 | 使用者 |
|------|------|------|--------|
| **buttplugio/buttplug** | 核心函式庫 | Rust 協議實現 | 開發者 |
| **intiface/intiface-central** | 前端應用 | 使用者界面 | 一般使用者 |

### 倉庫說明

#### buttplugio/buttplug (核心引擎)
- **功能**: Buttplug 協議的 Rust 核心實現
- **包含**: 客戶端、服務器、協議規範
- **路徑結構**:
  ```
  buttplugio/buttplug/
  ├── buttplug/              # Rust 核心實現
  ├── buttplug-schema/       # JSON 協議架構
  ├── buttplug-device-config/ # 設備配置
  └── buttplug_derive/       # 程序宏
  ```

#### intiface/intiface-central (前端應用)
- **功能**: 跨平台前端應用程式
- **技術**: Flutter + Rust 混合開發
- **平台**: Windows、macOS、Linux、Android、iOS
- **發佈**: 各大應用商店均有上架

---

## Flutter 整合方案

### 方案比較

| 方案 | 需要 Rust | 複雜度 | 推薦度 | 應用大小 |
|------|----------|--------|--------|----------|
| **Dart buttplug 套件 + Intiface Central** | ❌ | 低 | ⭐⭐⭐⭐⭐ | ~30MB |
| **FFI 直接整合** | ✅ | 高 | ⭐⭐ | ~120MB |
| **React Native + buttplug-js** | ❌ | 中 | ⭐⭐⭐ | ~50MB |

### 官方 Dart 套件 (推薦)

#### 安裝

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  buttplug: ^0.0.7  # 最新版本
```

#### 特點
- **純 Dart 實現**: 無需 FFI，無需外部依賴
- **協議支援**: 實現 Buttplug Message Spec v3
- **跨平台**: 支援所有 Flutter 平台
- **輕量級**: 不包含硬體協議實現

#### 基本使用

```dart
import 'package:buttplug/buttplug.dart';

// 初始化客戶端
final client = ButtplugClient('Flutter App');

// 連接到 Intiface Central
final connector = ButtplugWebsocketConnector(
  Uri.parse('ws://localhost:12345')
);
await client.connect(connector);

// 掃描設備
await client.startScanning();

// 控制設備
for (final device in client.devices) {
  if (device.allowedMessages.containsKey('VibrateCmd')) {
    await device.vibrate(0.5); // 50% 強度
  }
}
```

---

## 硬體支援情況

### Dart 套件的硬體支援機制

**重要**: Dart buttplug 套件本身不包含各家產品的具體協議，硬體支援完全由服務器端 (Intiface Central) 處理。

```
Flutter App (Dart) 發送: VibrateCmd(0.5)
         ↓
Intiface Central 轉換為設備特定命令:
  - Lovense: "Vibrate:10;"  
  - WeVibe: 特定藍牙封包
  - Kiiroo: 專屬協議格式
         ↓
實際藍牙設備
```

### 支援的設備品牌

#### 主要品牌
- **Lovense**: 全系列產品 (Max, Nora, Lush, Edge, Hush, Domi, Ambi, etc.)
- **Kiiroo**: Launch, Onyx, Pearl 系列
- **WeVibe**: Chorus, Sync, Pivot, Melt, Nova 等
- **The Handy**: 全自動撫摸設備
- **Satisfyer**: 部分型號 (需特定藍牙適配器)
- **Magic Motion**: 全系列
- **Svakom**: Sam, Alex, Iker 等

#### 連接方式支援
- **Bluetooth LE**: 主要連接方式，支援大部分現代設備
- **USB**: 直連設備支援
- **Serial**: 特殊設備如 E-Stim 系統
- **WebSocket**: 網路設備支援

### 完整設備清單

詳細的支援設備清單可查看: https://iostindex.com

---

## 各家產品 BT 命令位置

### 重要澄清

**Dart buttplug 套件不包含各家產品的 BT 命令**，這些實現都在 Rust 後端中。

### 程式碼結構

#### 1. 設備配置檔案
- **位置**: `https://github.com/buttplugio/buttplug-device-config`
- **檔案**: `buttplug-device-config.yml`
- **內容**: 設備名稱、藍牙服務/特徵值、連接參數

#### 2. 協議實現 (Rust)
- **位置**: `https://github.com/buttplugio/buttplug`
- **路徑**: `buttplug/src/server/device/protocol/`
- **檔案**:
  ```
  ├── lovense.rs          # Lovense 設備協議
  ├── kiiroo_v2.rs       # Kiiroo 第二代協議
  ├── kiiroo_v21.rs      # Kiiroo 2.1 協議
  ├── wevibe.rs          # WeVibe 協議
  ├── thehandy.rs        # The Handy 協議
  ├── vorze_sa.rs        # Vorze 協議
  └── ... (其他品牌)
  ```

#### 3. 藍牙底層支援
- **函式庫**: `btleplug` (跨平台藍牙 LE 庫)
- **位置**: `https://github.com/deviceplug/btleplug`

### 設備配置範例

```yaml
# buttplug-device-config.yml 片段
lovense:
  btle:
    names:
      - LVS-*
      - LOVE-*
    services:
      50300011-0023-4bd4-bbd5-a6920e4c5653:
        tx: 50300012-0023-4bd4-bbd5-a6920e4c5653
        rx: 50300013-0023-4bd4-bbd5-a6920e4c5653
```

### 資料流向

```
您的 Flutter App (Dart)
         ↓ WebSocket (標準 Buttplug 協議)
    Intiface Central
         ↓
    Buttplug Rust 服務器
         ↓
    協議處理模組 (lovense.rs, kiiroo.rs, etc.)
         ↓
    btleplug (跨平台藍牙庫)
         ↓ 
    實際藍牙設備
```

---

## APK/IPA 打包說明

### Android APK

#### 分離架構 (推薦)
```
您的 Flutter APK (~30MB)
├── Flutter 框架
├── Dart buttplug 客戶端套件
└── 您的應用程式碼

+ 

Intiface Central APK (單獨安裝 ~30MB)  
├── Flutter 框架
├── buttplug-rs (透過 FFI)
└── 各家設備協議實現
```

**特點**:
- ✅ 您的 APK 輕量
- ✅ 開發簡單
- ✅ 硬體支援由官方維護
- ❌ 需要安裝兩個應用

#### 整合架構 (不推薦)
```
單一 APK (~120MB)
├── Flutter 框架
├── 您的應用程式碼
├── Rust FFI 綁定
└── 完整 buttplug-rs 庫
```

**設定需求**:
```bash
# 添加 Android 目標
rustup target add aarch64-linux-android
rustup target add armv7-linux-androideabi
rustup target add x86_64-linux-android
rustup target add i686-linux-android
```

### iOS IPA

#### 分離架構 (推薦)
```
您的 iOS App (~30MB)
├── Flutter 框架  
├── Dart buttplug 客戶端套件
└── 您的應用程式碼

+

Intiface Central iOS App (App Store)
├── Flutter 框架
├── buttplug-rs (透過 FFI) 
└── 各家設備協議實現
```

#### 整合架構的額外挑戰
- ⚠️ App Store 審核更嚴格
- ⚠️ 需要詳細的隱私政策說明  
- ⚠️ 二進制大小限制
- ⚠️ 沙盒安全模型限制

---

## 平台特定注意事項

### Android

#### 權限配置
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.BLUETOOTH" />
<uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
```

#### 藍牙使用注意事項
- 🚫 **不要**在系統設定中配對設備
- ✅ 讓 Buttplug 直接發現和連接設備
- ⚠️ WeVibe/Satisfyer/Kiiroo 有特殊配對要求

### iOS

#### 權限配置
```xml
<!-- ios/Runner/Info.plist -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>This app connects to personal wellness devices via Bluetooth.</string>
<key>NSBluetoothPeripheralUsageDescription</key>
<string>This app manages connections to personal devices.</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>Location access is required for Bluetooth device discovery.</string>
```

#### 特殊限制
- 📱 背景執行限制嚴格
- 🔒 應用程式間通訊受限
- ⏰ 藍牙連線超時機制
- 🛡️ 沙盒安全模型

---

## 實作範例

### 基本 Flutter 整合

```dart
import 'package:flutter/material.dart';
import 'package:buttplug/buttplug.dart';

class ButtplugDemo extends StatefulWidget {
  @override
  _ButtplugDemoState createState() => _ButtplugDemoState();
}

class _ButtplugDemoState extends State<ButtplugDemo> {
  ButtplugClient? _client;
  bool _isConnected = false;
  bool _isScanning = false;
  List<ButtplugClientDevice> _devices = [];
  String _statusMessage = 'Not connected';

  @override
  void initState() {
    super.initState();
    _initializeClient();
  }

  void _initializeClient() {
    _client = ButtplugClient('Flutter Demo Client');
    
    // 設置事件監聽器
    _client!.deviceAdded = (device) {
      setState(() {
        _devices.add(device);
        _statusMessage = 'Device added: ${device.name}';
      });
    };
    
    _client!.deviceRemoved = (device) {
      setState(() {
        _devices.removeWhere((d) => d.index == device.index);
        _statusMessage = 'Device removed: ${device.name}';
      });
    };
    
    _client!.scanningFinished = () {
      setState(() {
        _isScanning = false;
        _statusMessage = 'Scanning finished';
      });
    };
  }

  Future<void> _connectToServer() async {
    try {
      final connector = ButtplugWebsocketConnector(
        Uri.parse('ws://localhost:12345')
      );
      
      await _client!.connect(connector);
      
      setState(() {
        _isConnected = true;
        _statusMessage = 'Connected to server';
      });
    } catch (e) {
      setState(() {
        _statusMessage = 'Connection failed: $e';
      });
    }
  }

  Future<void> _startScanning() async {
    if (!_isConnected) return;
    
    try {
      setState(() {
        _isScanning = true;
        _statusMessage = 'Scanning for devices...';
      });
      
      await _client!.startScanning();
    } catch (e) {
      setState(() {
        _isScanning = false;
        _statusMessage = 'Scanning failed: $e';
      });
    }
  }

  Future<void> _vibrateDevice(ButtplugClientDevice device, double intensity) async {
    try {
      if (device.allowedMessages.containsKey('VibrateCmd')) {
        await device.vibrate(intensity);
        setState(() {
          _statusMessage = 'Vibrating ${device.name} at ${(intensity * 100).toInt()}%';
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = 'Vibration failed: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Buttplug Flutter Demo')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 連接狀態卡片
            Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text('Connection Status', 
                         style: Theme.of(context).textTheme.titleLarge),
                    SizedBox(height: 8),
                    Text(_statusMessage,
                         style: TextStyle(
                           color: _isConnected ? Colors.green : Colors.red,
                         )),
                    SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        ElevatedButton(
                          onPressed: _isConnected ? null : _connectToServer,
                          child: Text('Connect'),
                        ),
                        ElevatedButton(
                          onPressed: _isScanning ? null : _startScanning,
                          child: Text('Scan Devices'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            // 設備列表
            if (_devices.isNotEmpty)
              Expanded(
                child: ListView.builder(
                  itemCount: _devices.length,
                  itemBuilder: (context, index) {
                    final device = _devices[index];
                    return DeviceCard(
                      device: device,
                      onVibrate: _vibrateDevice,
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class DeviceCard extends StatefulWidget {
  final ButtplugClientDevice device;
  final Function(ButtplugClientDevice, double) onVibrate;

  DeviceCard({required this.device, required this.onVibrate});

  @override
  _DeviceCardState createState() => _DeviceCardState();
}

class _DeviceCardState extends State<DeviceCard> {
  double _intensity = 0.0;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(vertical: 4.0),
      child: Padding(
        padding: EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(widget.device.name,
                 style: Theme.of(context).textTheme.titleMedium),
            SizedBox(height: 8),
            
            if (widget.device.allowedMessages.containsKey('VibrateCmd')) ...[
              Text('Intensity: ${(_intensity * 100).toInt()}%'),
              Slider(
                value: _intensity,
                onChanged: (value) {
                  setState(() => _intensity = value);
                  widget.onVibrate(widget.device, value);
                },
              ),
            ],
            
            ElevatedButton(
              onPressed: () => widget.device.stop(),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: Text('Stop', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 使用流程

1. **安裝 Intiface Central**
   - Android: Google Play Store
   - iOS: Apple App Store

2. **啟動 Intiface Central**
   - 開啟應用程式
   - 點擊 "Start Server"
   - 確保在 localhost:12345 運行

3. **運行您的 Flutter 應用程式**
   - 點擊 "Connect" 連接服務器
   - 點擊 "Scan Devices" 掃描設備
   - 使用滑桿控制設備

---

## 最佳實踐建議

### 開發建議

1. **架構選擇**
   - ✅ 優先使用 Dart buttplug + Intiface Central 方案
   - ❌ 避免複雜的 FFI 整合
   - 🎯 專注於應用邏輯而非硬體協議

2. **錯誤處理**
   ```dart
   try {
     await client.connect(connector);
   } catch (e) {
     if (e.toString().contains('Connection refused')) {
       // 提示用戶啟動 Intiface Central
     } else if (e.toString().contains('Bluetooth')) {
       // 提示用戶檢查藍牙權限
     }
   }
   ```

3. **使用者體驗**
   - 提供清晰的設定指南
   - 包含 Intiface Central 安裝連結
   - 實現友善的錯誤提示

### 發佈建議

1. **應用商店描述**
   - 避免過於明確的性相關描述
   - 重點強調「個人健康」、「按摩設備」
   - 提供詳細的隱私政策

2. **權限說明**
   - 詳細解釋為什麼需要藍牙權限
   - 說明位置權限的必要性 (iOS 要求)
   - 提供權限設定指南

3. **相容性測試**
   - 測試多種設備品牌
   - 驗證不同 Android/iOS 版本
   - 確保 Intiface Central 相容性

### 安全性考慮

1. **資料保護**
   - 不記錄敏感的使用資料
   - 使用本地連接 (WebSocket)
   - 避免雲端資料傳輸

2. **權限最小化**
   - 只請求必要的權限
   - 在需要時動態請求權限
   - 提供權限拒絕的降級功能

### 效能優化

1. **連接管理**
   ```dart
   // 應用暫停時斷開連接
   @override
   void didChangeAppLifecycleState(AppLifecycleState state) {
     if (state == AppLifecycleState.paused) {
       client?.disconnect();
     }
   }
   ```

2. **記憶體管理**
   - 適當釋放設備引用
   - 取消未完成的異步操作
   - 清理事件監聽器

---

## 總結

使用 **Dart buttplug 套件 + Intiface Central** 的組合是目前在 Flutter 中整合 Buttplug 的最佳方案：

### 優勢
- ✅ **開發簡單**: 純 Dart 實現，無需 Rust 知識
- ✅ **維護容易**: 硬體支援由官方維護
- ✅ **檔案小**: 應用程式保持輕量
- ✅ **跨平台**: Android/iOS 統一體驗
- ✅ **穩定可靠**: 經過大量用戶驗證

### 注意事項
- 📱 需要使用者安裝 Intiface Central
- 🔐 需要適當的權限配置
- 📋 需要詳細的使用說明

這個架構讓您可以專注於創建優秀的使用者體驗，而不需要擔心底層的硬體通訊複雜性。