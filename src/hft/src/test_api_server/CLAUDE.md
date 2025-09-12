# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

這是一個 API 效能測試套件，用於比較四種不同程式語言實作的非同步 HTTP 客戶端（Python、C、C++、Rust）連接到 Rust API 伺服器的效能表現。專案包含一個高效能的 Rust API 伺服器和四個客戶端實作，用於測試交易系統的延遲和吞吐量。

## Quick Start

```bash
# 1. Start the server
cd rust-api-server && cargo run --release &

# 2. Run a quick test with Python client
python3 python_client.py --orders 100 --connections 10 --warmup 10

# 3. Run each client individually for benchmarking
```

## Architecture

### Core Components

- **rust-api-server/**: Axum + Tokio 非同步 API 伺服器
  - 提供 `/order` 端點處理交易訂單
  - 追蹤客戶端/伺服器時間戳記以計算延遲
  - `/stats` 端點顯示效能統計

- **Client Implementations**:
  - `python_client.py`: aiohttp 非同步客戶端
  - `c-client/c_client.c`: libcurl + pthread 多執行緒客戶端
  - `cpp-client/cpp_client.cpp`: libcurl + std::async 客戶端  
  - `rust-client/`: reqwest + tokio 非同步客戶端

- **Performance Tools**:
  - `compare_performance.py`: 效能比較工具

## Prerequisites

### Required Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential cmake libcurl4-openssl-dev python3-pip

# macOS
brew install cmake curl

# Install Rust (all platforms)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Python dependencies
pip install aiohttp tabulate
```

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

### C Client
```bash
# 建構
cd c-client
make

# 執行
./c_client 1000 100 100  # orders connections warmup

# 快速測試
make test
```

### C++ Client
```bash
# 建構 (使用 Makefile)
cd cpp-client
make

# 或使用 CMake
mkdir -p build && cd build
cmake ..
make -j$(nproc)

# 執行
./cpp_client 1000 100 100  # orders connections warmup

# 快速測試
make test
```

### Rust Client
```bash
# 建構並執行
cd rust-client
cargo run --release -- --orders 1000 --connections 100 --warmup 100

# 開發模式
cargo run -- --orders 100 --connections 10 --warmup 10
```


## Testing Commands

### 單一客戶端測試
```bash
# Python 客戶端單元測試（如有）
python3 -m pytest python_client.py -v

# Rust 測試
cd rust-api-server && cargo test
cd rust-client && cargo test

# C 測試
cd c-client && make test

# C++ 測試
cd cpp-client && make test
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
├── c-client/            # C 客戶端
│   ├── c_client.c       # C 客戶端主程式
│   └── Makefile         # C 建構設定
├── cpp-client/          # C++ 客戶端
│   ├── cpp_client.cpp   # C++ 客戶端主程式
│   ├── Makefile         # C++ 建構設定
│   └── CMakeLists.txt   # CMake 建構設定
├── python_client.py     # Python 客戶端
└── compare_performance.py # 效能比較工具
```

## Key API Endpoints

### POST /order
- 接收交易訂單請求
- 計算客戶端到伺服器的延遲
- 回傳處理狀態和時間戳記

**Request Format:**
```json
{
  "order_id": "ORDER_001",
  "symbol": "BTCUSDT",
  "quantity": 1,
  "price": 50000.0,
  "side": "BUY",
  "client_timestamp": "2024-01-01T10:00:00.000Z"
}
```

**Response Format:**
```json
{
  "order_id": "ORDER_001",
  "status": "ACCEPTED",
  "client_timestamp": "2024-01-01T10:00:00.000Z",
  "server_timestamp": "2024-01-01T10:00:00.010Z",
  "latency_ms": 10.0
}
```

### GET /stats  
- 取得伺服器統計資料
- 顯示總訂單數和吞吐量

**Response Format:**
```json
{
  "total_orders": 5000,
  "elapsed_seconds": 5.23,
  "orders_per_second": 956.02
}
```

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

### 建構所有客戶端
```bash
# 一次建構所有客戶端
cd c-client && make && cd ..
cd cpp-client && make && cd ..
cd rust-client && cargo build --release && cd ..
```

### 清理建構產物
```bash
# 清理所有建構產物
cd c-client && make clean && cd ..
cd cpp-client && make clean && cd ..
cd rust-client && cargo clean && cd ..
cd rust-api-server && cargo clean && cd ..
```

### 修改伺服器埠號
編輯 `rust-api-server/src/main.rs` 中的：
```rust
let addr = SocketAddr::from(([127, 0, 0, 1], 8080));  // 修改 8080
```

### 調整客戶端超時設定
- Python: 修改 `python_client.py` 中的 `timeout` 參數
- C: 調整 `c-client/c_client.c` 中的 `CURLOPT_TIMEOUT`
- C++: 調整 `cpp-client/cpp_client.cpp` 中的 `CURLOPT_TIMEOUT`
- Rust: 修改 `rust-client/src/main.rs` 中的 `timeout` 設定

### 新增效能指標
1. 在客戶端收集新指標
2. 更新輸出格式以包含新指標
3. 修改 `compare_performance.py` 以解析新指標

## Troubleshooting

### 常見問題
- **Port already in use**: 使用 `lsof -i :8080` 檢查並 `kill -9 <PID>` 終止佔用程序
- **Too many open files**: 執行 `ulimit -n 65536` 增加檔案描述符限制
- **libcurl not found**: 安裝 `libcurl4-openssl-dev` (Ubuntu) 或 `curl` (macOS)
- **Performance issues**: 確保使用 release 模式編譯 (`--release` for Rust, `-O3` for C/C++)