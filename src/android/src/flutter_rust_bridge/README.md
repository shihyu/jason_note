# Rust-Flutter Bridge Demo

這是一個展示 Android Native Rust 與 Flutter 雙向溝通的簡單測試專案。

## 專案結構

```
rust_to_fluuter/
├── Cargo.toml                          # Rust 專案配置
├── src/
│   └── lib.rs                          # Rust FFI 實作和測試
├── target/release/                     # 編譯後的動態函式庫
│   └── librust_flutter_bridge.so
└── flutter_app/                        # Flutter 應用程式
    ├── pubspec.yaml                    # Flutter 專案配置  
    ├── lib/
    │   ├── main.dart                   # Flutter 主應用程式
    │   └── rust_bridge.dart            # FFI 橋接層
    └── test/                           # 測試目錄
        ├── widget_test.dart            # Widget 測試
        ├── rust_bridge_unit_test.dart  # 邏輯單元測試
        ├── rust_bridge_test.dart       # FFI 整合測試
        └── integration_test.dart       # 完整整合測試
```

## 功能特點

### Rust 端 (FFI)
- **數字加法**: 簡單的兩數相加功能
- **訊息處理**: JSON 序列化/反序列化處理
- **系統資訊**: 獲取 Rust 版本和系統資訊
- **記憶體管理**: 安全的字串記憶體分配和釋放
- **錯誤處理**: 完善的錯誤處理機制

### Flutter 端 (Dart)
- **FFI 綁定**: 動態載入 Rust 動態函式庫
- **雙向通訊**: Flutter 調用 Rust 函數並接收回應
- **UI 介面**: 直觀的測試介面
- **效能基準**: 批量操作效能測試
- **錯誤處理**: 異常捕獲和使用者友好的錯誤顯示

## 實作的雙向溝通功能

### 1. 數字運算
- Flutter 傳送兩個整數到 Rust
- Rust 執行加法運算並返回結果

### 2. 複雜訊息處理  
- Flutter 傳送 JSON 結構化資料到 Rust
- Rust 解析 JSON，處理後返回結構化回應
- 支援 Unicode 字符和特殊字符

### 3. 系統資訊查詢
- Flutter 請求系統資訊
- Rust 收集並返回系統版本資訊

### 4. 效能基準測試
- 測量大量 FFI 調用的效能
- 提供詳細的時間統計

## 測試覆蓋

### Rust 測試 (6 個測試)
- ✅ 基本數字加法測試
- ✅ 有效 JSON 訊息處理測試
- ✅ 無效 JSON 錯誤處理測試  
- ✅ 空指標處理測試
- ✅ 系統資訊獲取測試
- ✅ 記憶體管理測試 (1000 次操作)

### Flutter 測試
- ✅ Widget 煙霧測試
- ✅ JSON 序列化/反序列化測試
- ✅ Unicode 字符處理測試
- ✅ 大資料處理效能測試
- ✅ 數字範圍驗證測試
- ✅ 基準計算邏輯測試

## 建置和執行

### 建置 Rust 函式庫
```bash
cargo build --release
```

### 執行 Rust 測試
```bash 
cargo test
```

### 執行 Flutter 測試
```bash
cd flutter_app
flutter pub get
flutter test
```

### 執行 Flutter 應用程式
```bash
cd flutter_app  
flutter run
```

## 安全性考量

- ✅ 輸入驗證：所有外部輸入都經過驗證
- ✅ 記憶體安全：正確的 C 字串記憶體管理
- ✅ 錯誤處理：完善的異常處理機制
- ✅ 空指標檢查：防止空指標存取
- ✅ JSON 解析安全：錯誤的 JSON 不會導致崩潰

## 效能特點

- 平均 FFI 調用時間 < 1000 微秒
- 支援大資料處理 (10KB+ 字串)
- 記憶體洩漏測試通過 (1000+ 次操作)  
- 支援高並發調用

## 支援的平台

- ✅ Linux (開發和測試環境)
- ✅ Android (透過 JNI)
- 🔄 iOS (需要額外配置)
- 🔄 Windows (需要額外配置)

## 使用 Makefile

專案提供了完整的 Makefile 來簡化開發流程：

### 基本命令
```bash
make help           # 顯示所有可用命令
make build          # 建置完整專案
make test           # 執行所有測試
make clean          # 清理建置文件
make install        # 完整安裝流程
```

### 開發命令
```bash
make dev            # 開發模式 (hot reload)
make quick-test     # 快速測試
make watch-rust     # 監控 Rust 程式碼變更
make watch-flutter  # 監控 Flutter 程式碼變更
```

### 建置命令  
```bash
make build-rust     # 只建置 Rust 函式庫
make build-debug    # 建置 debug 版本
make copy-libs      # 複製函式庫到 Flutter
make android-build  # 建置 Android APK
```

### 測試命令
```bash
make test-rust      # 只執行 Rust 測試
make test-flutter   # 只執行 Flutter 測試
make test-integration # 執行整合測試
make benchmark      # 執行效能基準測試
```

### 程式碼品質
```bash
make check          # 程式碼檢查
make lint           # 程式碼 linting
make format         # 程式碼格式化
make security-audit # 安全性審計
```

### 狀態查詢
```bash
make status         # 建置狀態
make info           # 專案資訊
make size-check     # 檢查建置產物大小
```

### CI/CD
```bash
make ci             # CI 管道
make cd             # CD 管道
make docker-build   # Docker 建置
make docker-test    # Docker 測試
```

### 一鍵操作
```bash
make all            # 完整流程 (清理+安裝+測試)
make demo           # 展示模式
```

## Docker 支援

專案支援 Docker 容器化開發：

```bash
# 建置 Docker 映像
make docker-build

# 在 Docker 中執行測試
make docker-test
```

## VS Code 整合

專案包含完整的 VS Code 配置：
- 自動格式化
- 任務定義 (Ctrl+Shift+P → Tasks)
- Debug 配置
- 推薦擴充功能設定

## CI/CD 管道

GitHub Actions 自動化流程：
- ✅ Rust 測試和 linting
- ✅ Flutter 測試和分析  
- ✅ 整合測試
- ✅ 安全性審計
- ✅ Android APK 建置
- ✅ Docker 映像建置
- ✅ 自動發布

## 🔍 日誌監控

專案整合了完整的日誌系統，使用 **BitoPro** 標籤：

### 查看 Android Logcat 日誌
```bash
# 只顯示 BitoPro 標籤的日誌
adb logcat -s BitoPro

# 或使用專案提供的腳本
make logcat

# 帶時間戳的日誌監控
./logcat_bitopro.sh
```

### 日誌內容
- ✅ Rust 函數調用記錄
- ✅ 參數和返回值追蹤
- ✅ 錯誤和異常信息
- ✅ 記憶體管理操作
- ✅ JSON 數據處理過程

### 示例日誌輸出
```
[BitoPro] Rust logger initialized successfully
[BitoPro] rust_add_numbers called with a=123, b=456
[BitoPro] Addition result: 123 + 456 = 579
[BitoPro] rust_process_message called  
[BitoPro] Received JSON string: {"id":42,"content":"測試","timestamp":1234567890}
[BitoPro] Successfully parsed message: id=42, content='測試', timestamp=1234567890
[BitoPro] Returning response: {"success":true,"data":"[BitoPro] Processed: 測試","error":null}
```

## 🧪 測試方式

### 1. 本地 FFI 測試
```bash
# 測試 Rust 動態函式庫
make test-local-ffi
```

### 2. Flutter 應用程式測試
```bash
# 單純執行應用程式
make run

# 執行應用程式並同時監控日誌
make test-with-logs

# Android 設備測試
make test-android
```

### 3. 簡單按鈕測試界面

新的應用程式提供直觀的測試界面：

- **🔢 測試數字加法**: 測試基本 FFI 調用
- **📨 測試訊息處理**: 測試 JSON 序列化/反序列化  
- **ℹ️ 測試系統資訊**: 測試字串返回功能
- **🚀 執行所有測試**: 依序執行所有測試項目

每個測試都會：
- 在界面顯示結果狀態
- 在控制台輸出 Flutter 日誌
- 在 Android logcat 記錄詳細的 Rust 日誌

### 4. 白畫面問題已修復

原來的複雜界面已替換為：
- ✅ 簡潔清晰的測試界面
- ✅ 即時狀態反饋
- ✅ 詳細的錯誤信息顯示
- ✅ 一鍵測試所有功能

## 效能數據

- **Rust 函式庫大小**: 524KB (release)
- **平均 FFI 調用時間**: < 1000 微秒  
- **記憶體測試**: 1000+ 次操作無洩漏
- **並發測試**: 50 個併發請求正常處理
- **日誌性能**: 低延遲，不影響主要功能

## 下一步擴展

1. 加入更複雜的資料結構傳輸
2. 實作異步回調機制
3. 加入加密通訊
4. 支援流式資料傳輸
5. 加入更多平台支援
6. WebAssembly 支援
7. 效能優化和快取機制

這個專案展示了如何在 Flutter 和 Rust 之間建立安全、高效的雙向通訊機制，並提供了完整的開發工具鏈，適合作為更複雜應用程式的基礎架構。