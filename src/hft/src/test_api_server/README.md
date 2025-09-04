# API 效能測試套件

本專案比較三種不同的非同步 HTTP 客戶端（Python、C++、Rust）連接到基於 Rust 的 API 伺服器的效能表現。

## 專案結構

```
test_api_server/
├── rust-api-server/    # 使用 Axum 的 Rust API 伺服器
├── rust-client/        # 使用 reqwest + tokio 的 Rust 非同步客戶端
├── python_client.py    # 使用 aiohttp 的 Python 非同步客戶端
├── cpp_client.cpp      # 使用 libcurl 的 C++ 非同步客戶端
├── CMakeLists.txt      # C++ 建構設定
└── run_benchmark.sh    # 自動化基準測試腳本
```

## 功能特色

- **Rust API 伺服器**：使用 Axum 和 Tokio 建構的高效能非同步伺服器
- **三種客戶端實作**：
  - Python 使用 aiohttp (async/await)
  - C++ 使用 libcurl 和 std::async
  - Rust 使用 reqwest 和 tokio
- **延遲追蹤**：測量網路往返時間和伺服器處理時間
- **效能指標**：吞吐量、延遲百分位數（P50、P90、P95、P99）

## 系統需求

### 系統需求
- Linux/macOS（已在 Ubuntu 20.04+ 上測試）
- 建議 4 個以上 CPU 核心
- 建議 8GB 以上記憶體

### 軟體相依套件

#### Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### Python
```bash
pip install aiohttp
```

#### C++
```bash
# Ubuntu/Debian
sudo apt-get install build-essential cmake libcurl4-openssl-dev

# macOS
brew install cmake curl
```

## 快速開始

### 1. 啟動 API 伺服器
```bash
cd rust-api-server
cargo run --release
```
伺服器將在 `http://localhost:8080` 上啟動

### 2. 執行個別客戶端

#### Python 客戶端
```bash
python3 python_client.py --orders 1000 --connections 100 --warmup 100
```

#### C++ 客戶端
```bash
mkdir build && cd build
cmake .. && make
./cpp_client 1000 100 100
```

#### Rust 客戶端
```bash
cd rust-client
cargo run --release -- --orders 1000 --connections 100 --warmup 100
```

### 3. 執行自動化基準測試
```bash
chmod +x run_benchmark.sh
./run_benchmark.sh
```

## API 端點

### POST /order
提交帶有時間戳記追蹤的交易訂單。

請求：
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

回應：
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
取得伺服器效能統計資料。

回應：
```json
{
  "total_orders": 5000,
  "elapsed_seconds": 5.23,
  "orders_per_second": 956.02
}
```

## 效能指標說明

- **往返延遲**：從客戶端請求到回應的總時間
- **伺服器延遲**：客戶端和伺服器時間戳記之間的時間差
- **吞吐量**：每秒處理的訂單數
- **百分位數**：P50（中位數）、P90、P95、P99 延遲分佈

## 調校參數

### 客戶端設定
- `--orders`：要傳送的訂單總數
- `--connections`：並行連線數
- `--warmup`：暖身訂單數（不計入統計）

### 伺服器設定
編輯 `rust-api-server/src/main.rs` 來調整：
- 連接埠號（預設：8080）
- 日誌層級
- CORS 設定

## 預期結果

在現代系統上的典型效能（Intel i7、16GB RAM）：

| 客戶端 | 吞吐量 (訂單/秒) | P50 延遲 (毫秒) | P99 延遲 (毫秒) |
|--------|-----------------|----------------|----------------|
| Rust   | 15,000-20,000   | 5-10           | 20-30          |
| Python | 5,000-8,000     | 15-25          | 50-80          |
| C++    | 10,000-15,000   | 8-15           | 30-50          |

*結果會因系統規格和負載而異*

## 疑難排解

### 伺服器無法啟動
- 檢查連接埠 8080 是否已被使用：`lsof -i :8080`
- 終止現有程序：`kill -9 <PID>`

### C++ 客戶端編譯錯誤
- 確保已安裝 libcurl-dev
- 檢查 CMake 版本：`cmake --version`（需要 3.10+）

### Python 客戶端錯誤
- 安裝 aiohttp：`pip install aiohttp`
- 檢查 Python 版本：`python3 --version`（需要 3.7+）

### 效能低落
- 以 release 模式執行伺服器：`cargo run --release`
- 增加檔案描述符限制：`ulimit -n 65536`
- 檢查 CPU 調速器：`cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`

## 授權

MIT