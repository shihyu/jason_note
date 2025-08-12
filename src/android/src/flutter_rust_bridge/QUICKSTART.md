# 快速開始指南 🚀

## 前置需求

確保您已安裝以下工具：

- **Rust** (1.70+): `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **Flutter** (3.24+): [安裝指南](https://docs.flutter.dev/get-started/install)
- **Make**: `sudo apt install make` (Linux) 或 `brew install make` (macOS)

## 一鍵安裝

```bash
# 克隆專案
git clone <repository-url>
cd rust_to_fluuter

# 完整安裝 (建置 + 測試)
make all
```

## 快速測試

```bash
# 執行所有測試
make test

# 或者只執行快速測試
make quick-test
```

## 執行應用程式

```bash
# 開發模式 (支援 hot reload)
make dev

# 或者正常模式
make run
```

## 常用命令

| 命令 | 說明 |
|------|------|
| `make help` | 查看所有可用命令 |
| `make status` | 檢查專案狀態 |
| `make build` | 建置專案 |
| `make clean` | 清理建置文件 |
| `make test` | 執行測試 |

## 專案結構

```
rust_to_fluuter/
├── Makefile              # 建置和任務管理
├── Cargo.toml           # Rust 專案配置
├── src/lib.rs           # Rust FFI 實作
├── flutter_app/         # Flutter 應用程式
│   ├── lib/main.dart    # Flutter 主程式
│   ├── lib/rust_bridge.dart # FFI 橋接層
│   └── test/            # Flutter 測試
├── .github/workflows/   # CI/CD 配置
├── .vscode/            # VS Code 配置
└── README.md           # 詳細文件
```

## 測試 FFI 功能

1. **數字加法測試**:
   - 在 Flutter UI 中輸入兩個數字
   - 點擊「Add Numbers」按鈕
   - 查看 Rust 計算結果

2. **訊息處理測試**:
   - 輸入文字訊息 (支援中文、Emoji)
   - 點擊「Process Message」按鈕
   - 查看 Rust 處理後的 JSON 回應

3. **系統資訊測試**:
   - 點擊「Refresh System Info」按鈕
   - 查看從 Rust 獲取的系統資訊

4. **效能基準測試**:
   - 點擊「Run Benchmark」按鈕
   - 查看 1000 次 FFI 調用的效能數據

## 開發模式

```bash
# 啟動開發模式 (支援熱重載)
make dev

# 另開終端監控 Rust 變更
make watch-rust

# 另開終端監控 Flutter 變更  
make watch-flutter
```

## 疑難排解

### 問題：找不到動態函式庫
```bash
# 確保函式庫已建置和複製
make build
make copy-libs
```

### 問題：Flutter 測試失敗
```bash
# 重新安裝依賴
make clean
make flutter-deps
```

### 問題：Rust 編譯錯誤
```bash
# 檢查 Rust 工具鏈
rustc --version
cargo --version

# 更新工具鏈
rustup update
```

## VS Code 整合

如果使用 VS Code：

1. 安裝推薦擴充功能：
   - Rust Analyzer
   - Flutter
   - Dart

2. 使用內建任務：
   - `Ctrl+Shift+P` → `Tasks: Run Task`
   - 選擇預定義任務 (Build Rust, Test, Run App 等)

3. 使用 Debug 配置：
   - `F5` 啟動 Flutter 應用程式 Debug
   - 自動建置 Rust 函式庫

## 進階功能

### Android 建置
```bash
make android-build
```

### Docker 開發
```bash
make docker-build
make docker-test
```

### 程式碼品質檢查
```bash
make check
make lint
make format
```

### 效能分析
```bash
make benchmark
make profile
```

## 獲取幫助

- 查看完整文件: `cat README.md`
- 查看所有命令: `make help`
- 檢查專案狀態: `make status`
- 查看專案資訊: `make info`

## 下一步

完成快速開始後，您可以：

1. 修改 `src/lib.rs` 加入更多 Rust 功能
2. 修改 `flutter_app/lib/main.dart` 改進 UI
3. 加入更多測試案例
4. 探索交叉編譯和部署選項

祝您開發愉快！🎉