# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

這是一個 API 效能測試套件，用於比較五種不同程式語言實作的非同步 HTTP 客戶端（Python、C、C++、Rust、Go）連接到 Rust API 伺服器的效能表現。專案包含一個高效能的 Rust API 伺服器和五個客戶端實作，用於測試交易系統的延遲和吞吐量。

### Performance Focus
此專案專注於高頻交易(HFT)系統的低延遲優化，目標是將延遲控制在微秒級別。C 客戶端已經過線程池優化，從原始的 pthread-per-connection 模式改為固定大小線程池，P99 延遲從 23.65ms 降至 0.70ms。

## Quick Start

```bash
# 1. Start the server
cd rust-api-server && cargo run --release &

# 2. Run a quick test with Python client
python3 python_client.py --orders 100 --connections 10 --warmup 10

# 3. Run complete performance comparison (builds all clients and generates plots)
make plot

# 4. Run individual clients for specific testing
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
  - `go-client/go_client.go`: Go net/http 標準庫客戶端

- **Performance Tools**:
  - `compare_performance.py`: 效能比較工具

## Prerequisites

### Required Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential cmake libcurl4-openssl-dev python3-pip golang

# macOS
brew install cmake curl go

# Install Rust (all platforms)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Go (if not installed via package manager)
# Download from https://go.dev/dl/ or use:
wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

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

### Go Client
```bash
# 建構
cd go-client
go build -o go_client go_client.go

# 或使用 Makefile
make

# 執行
./go_client --orders 1000 --connections 100 --warmup 100

# 快速測試
make test
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

# Go 測試
cd go-client && go test
```

### 效能比較測試
```bash
# 執行完整效能比較（包含圖表生成）
python3 compare_performance.py

# 快速測試（較少訂單數）
python3 quick_test.py

# 檢查伺服器運行狀態
curl http://localhost:8080/stats | python3 -m json.tool
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
├── go-client/           # Go 客戶端
│   ├── go_client.go     # Go 客戶端主程式
│   ├── go.mod          # Go 模組定義
│   └── Makefile        # Go 建構設定
├── python_client.py     # Python 客戶端
└── compare_performance.py # 效能比較工具
```

## Key API Endpoints

### POST /order
- 接收交易訂單請求
- 計算客戶端到伺服器的延遲
- 回傳處理狀態和時間戳記

**Request Format (Updated for HFT):**
```json
{
  "buy_sell": "buy",
  "symbol": 2330,
  "price": 100.0,
  "quantity": 1000,
  "market_type": "common",
  "price_type": "limit",
  "time_in_force": "rod",
  "order_type": "stock",
  "user_def": "custom_field",
  "client_timestamp": "2024-01-01T10:00:00.000Z"
}
```

**Response Format:**
```json
{
  "symbol": 2330,
  "buy_sell": "buy",
  "status": "SUCCESS",
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

# 關閉透明大頁（減少延遲抖動）
sudo sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled'

# CPU 隔離（用於極低延遲測試）
# 編輯 /etc/default/grub 並添加：
# isolcpus=8-15 nohz_full=8-15 rcu_nocbs=8-15
```

### HFT 系統優化重點
- **核心隔離**：將關鍵執行緒綁定到專用 CPU 核心
- **NUMA 優化**：確保記憶體分配在本地節點
- **記憶體鎖定**：使用 mlock 防止換頁
- **中斷處理**：將網路中斷重定向到非關鍵核心

### 客戶端參數
- `--orders`: 總訂單數
- `--connections`: 並發連線數
- `--warmup`: 暖身訂單數（不計入統計）

## Development Notes

### 重要考量
- 所有客戶端都使用非同步 I/O 以達到最佳效能
- 時間戳記使用 ISO 8601 格式確保跨語言相容性
- Release 模式編譯對效能至關重要（Rust 和 C++）
- C 客戶端使用固定大小線程池（最多 20 個工作線程）避免過度的上下文切換

### 效能指標
- **吞吐量**：每秒處理的訂單數
- **延遲百分位數**：P50、P90、P95、P99
- **往返時間**：完整的請求-回應時間
- **伺服器處理時間**：基於時間戳記差異計算

### 已知優化
- **C 客戶端線程池**：從 pthread-per-connection 改為固定線程池，P99 延遲降低 97%
- **連接池**：所有客戶端實現連接複用以減少建立連接開銷
- **批量處理**：支援批量發送訂單以提高吞吐量

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
make build

# 或手動建構（使用平行建構）
make -j$(nproc) -C c-client &
make -j$(nproc) -C cpp-client &
(cd rust-client && cargo build --release) &
(cd go-client && go build -o go_client go_client.go) &
wait
echo "All clients built successfully"
```

### 清理建構產物
```bash
# 清理所有建構產物
make clean

# 或手動清理
cd c-client && make clean && cd ..
cd cpp-client && make clean && cd ..
cd rust-client && cargo clean && cd ..
cd go-client && make clean && cd ..
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
- Go: 修改 `go-client/go_client.go` 中的 `http.Client` 的 `Timeout` 設定

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
- **High P99 latency with C client**: 確認線程池實作已啟用（檢查 MAX_THREADS 設定）
- **Server not responding**: 檢查伺服器是否在執行 `ps aux | grep rust-api-server`

## Performance Benchmarking Best Practices

### 測試前準備
```bash
# 1. 確保系統處於穩定狀態
sudo systemctl stop snapd  # 停止非必要服務
sudo systemctl stop bluetooth

# 2. 設定 CPU 效能模式
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
  echo performance | sudo tee $i
done

# 3. 清理系統快取（可選）
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
```

### 標準測試配置
- **小型測試**：100 orders, 10 connections（用於快速驗證）
- **中型測試**：1000 orders, 50 connections（用於開發測試）
- **大型測試**：10000 orders, 100 connections（用於效能基準）
- **壓力測試**：50000 orders, 200 connections（用於極限測試）

### 關鍵效能指標解讀
- **P50 < 0.5ms**：良好的中位數延遲
- **P99 < 2ms**：可接受的尾部延遲
- **P99.9 < 10ms**：極端情況下的延遲上限
- **Throughput > 10K req/s**：基本的吞吐量要求

## HFT-Specific Documentation

### 相關文檔
- `hft_cpp.md`：詳細的 HFT 系統優化指南（中文）
- `C_CLIENT_THREAD_POOL_OPTIMIZATION.md`：C 客戶端線程池優化案例研究
- `C_CLIENT_THREAD_POOL_OPTIMIZATION_TC.md`：線程池優化技術細節

### 深度優化參考
如需進行更深入的 HFT 優化，請參考 `hft_cpp.md` 文檔中的以下章節：
- 核心隔離技術
- NUMA 記憶體優化
- 缺頁中斷優化
- 快取優化策略

## Important Commands Summary

### Complete Performance Test Workflow
```bash
# Full automated test with plots
make plot  # Builds all, starts server, runs tests, generates plots, stops server

# Manual step-by-step
make build                    # Build all clients
cd rust-api-server && cargo run --release &  # Start server
python3 compare_performance.py  # Run comparison tests
python3 quick_test.py         # Quick test with smaller dataset
kill $(lsof -ti:8080)         # Stop server
```

### Individual Client Testing
```bash
# C Client
cd c-client && make test  # Quick test
./c_client 1000 100 100    # Full test: orders connections warmup

# C++ Client
cd cpp-client && make test
./cpp_client_hft 1000 100 100

# Rust Client
cd rust-client && cargo test
cargo run --release -- --orders 1000 --connections 100 --warmup 100

# Go Client
cd go-client && make test
./go_client --orders 1000 --connections 100 --warmup 100

# Python Client
python3 python_client.py --orders 1000 --connections 100 --warmup 100
```

### Linting and Type Checking
```bash
# Rust projects
cd rust-api-server && cargo clippy -- -D warnings && cargo fmt --check
cd rust-client && cargo clippy -- -D warnings && cargo fmt --check

# Go
cd go-client && go fmt ./... && go vet ./...

# C/C++ (if cppcheck is installed)
cppcheck --enable=all c-client/c_client.c
cppcheck --enable=all --language=c++ cpp-client/cpp_client_hft.cpp

# Python (if pylint/black installed)
pylint python_client.py compare_performance.py
black --check *.py
```

## Architecture Deep Dive

### Cross-Language Performance Testing Pattern
The project follows a consistent pattern across all client implementations:
1. **Connection Pool Management**: All clients maintain a pool of persistent HTTP connections
2. **Timestamp Tracking**: ISO 8601 format timestamps for cross-language compatibility
3. **Warmup Phase**: Initial requests excluded from statistics to ensure steady state
4. **Percentile Calculation**: Consistent latency percentile reporting (P50, P90, P95, P99)

### Critical Performance Paths
- **Server**: Axum's async handlers with shared state via Arc<Mutex<>>
- **C Client**: Thread pool with work queue pattern, NUMA-aware memory allocation
- **C++ Client**: std::async with futures, AVX2 optimizations for data processing
- **Rust Client**: Tokio runtime with connection pooling via reqwest
- **Go Client**: Goroutine pool with channel-based work distribution
- **Python Client**: aiohttp with asyncio event loop

### Build Optimization Flags
- **C/C++**: `-O3 -march=native -mtune=native` for maximum CPU-specific optimizations
- **Rust**: `--release` mode enables all optimizations including LTO
- **Go**: `CGO_ENABLED=0` for static binary, `-ldflags="-s -w"` for size reduction

## Known Issues and Gotchas

- **NUMA Libraries**: C/C++ clients require libnuma-dev for optimal performance
- **File Descriptor Limits**: High connection counts require `ulimit -n 65536`
- **CPU Governor**: Must be set to 'performance' for consistent benchmarking
- **Server Warmup**: First few requests after server start may show higher latency
- **Go Client Garbage Collection**: May cause latency spikes; consider GOGC tuning
- **Python GIL**: Despite async I/O, Python client may bottleneck on CPU-bound operations