# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

這是一個 API 效能測試套件，用於比較三種不同程式語言實作的非同步 HTTP 客戶端（Python、C++、Rust）連接到 Rust API 伺服器的效能表現。專案包含一個高效能的 Rust API 伺服器和三個客戶端實作，用於測試交易系統的延遲和吞吐量。

## Architecture

### Core Components

- **rust-api-server/**: Axum + Tokio 非同步 API 伺服器
  - 提供 `/order` 端點處理交易訂單
  - 追蹤客戶端/伺服器時間戳記以計算延遲
  - `/stats` 端點顯示效能統計

- **Client Implementations**:
  - `python_client.py`: aiohttp 非同步客戶端
  - `cpp_client.cpp`: libcurl + std::async 客戶端  
  - `rust-client/`: reqwest + tokio 非同步客戶端

- **Performance Tools**:
  - `run_benchmark.sh`: 自動化基準測試腳本
  - `compare_performance.py`: 效能比較工具

## Build and Run Commands

### Server
```bash
# 建構並執行伺服器（release 模式）
cd rust-api-server
cargo run --release

# 開發模式
cargo run
```

### Python Client
```bash
# 安裝依賴
pip install aiohttp

# 執行測試
python3 python_client.py --orders 1000 --connections 100 --warmup 100
```

### C++ Client
```bash
# 建構
mkdir -p build && cd build
cmake ..
make -j$(nproc)

# 執行
./build/cpp_client 1000 100 100  # orders connections warmup
```

### Rust Client
```bash
# 建構並執行
cd rust-client
cargo run --release -- --orders 1000 --connections 100 --warmup 100

# 開發模式
cargo run -- --orders 100 --connections 10 --warmup 10
```

### Automated Benchmark
```bash
# 執行完整基準測試（會自動建構所有客戶端）
chmod +x run_benchmark.sh
./run_benchmark.sh
```

## Testing Commands

### 單一客戶端測試
```bash
# Python 客戶端單元測試（如有）
python3 -m pytest python_client.py -v

# Rust 測試
cd rust-api-server && cargo test
cd rust-client && cargo test

# C++ 測試（透過執行檔）
./build/cpp_client 10 1 0  # 小規模快速測試
```

### 效能比較測試
```bash
# 執行效能比較腳本
python3 compare_performance.py
```

## Project Structure

```
test_api_server/
├── rust-api-server/      # Rust API 伺服器
│   ├── src/
│   │   └── main.rs      # 伺服器主程式
│   └── Cargo.toml       # Rust 依賴設定
├── rust-client/         # Rust 客戶端
│   ├── src/
│   │   └── main.rs      # 客戶端主程式
│   └── Cargo.toml       # Rust 依賴設定
├── python_client.py     # Python 客戶端
├── cpp_client.cpp       # C++ 客戶端
├── CMakeLists.txt       # C++ 建構設定
├── run_benchmark.sh     # 自動化測試腳本
└── compare_performance.py # 效能比較工具
```

## Key API Endpoints

### POST /order
- 接收交易訂單請求
- 計算客戶端到伺服器的延遲
- 回傳處理狀態和時間戳記

### GET /stats  
- 取得伺服器統計資料
- 顯示總訂單數和吞吐量

## Performance Tuning

### 系統優化
```bash
# 增加檔案描述符限制（適用於高並發測試）
ulimit -n 65536

# 檢查 CPU 調速器設定
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 設定為高效能模式
sudo cpupower frequency-set -g performance
```

### 客戶端參數
- `--orders`: 總訂單數
- `--connections`: 並發連線數
- `--warmup`: 暖身訂單數（不計入統計）

## Development Notes

### 重要考量
- 所有客戶端都使用非同步 I/O 以達到最佳效能
- 時間戳記使用 ISO 8601 格式確保跨語言相容性
- Release 模式編譯對效能至關重要（Rust 和 C++）

### 效能指標
- **吞吐量**：每秒處理的訂單數
- **延遲百分位數**：P50、P90、P95、P99
- **往返時間**：完整的請求-回應時間
- **伺服器處理時間**：基於時間戳記差異計算

### 除錯
```bash
# 啟用 Rust 詳細日誌
RUST_LOG=debug cargo run

# 檢查伺服器狀態
curl http://localhost:8080/stats | python3 -m json.tool

# 監控系統資源
htop  # CPU 和記憶體使用率
iotop # I/O 活動
```

## Common Tasks

### 修改伺服器埠號
編輯 `rust-api-server/src/main.rs` 中的：
```rust
let addr = SocketAddr::from(([127, 0, 0, 1], 8080));  // 修改 8080
```

### 調整客戶端超時設定
- Python: 修改 `python_client.py` 中的 `timeout` 參數
- C++: 調整 `cpp_client.cpp` 中的 `CURLOPT_TIMEOUT`
- Rust: 修改 `rust-client/src/main.rs` 中的 `timeout` 設定

### 新增效能指標
1. 在客戶端收集新指標
2. 更新輸出格式以包含新指標
3. 修改 `compare_performance.py` 以解析新指標