# API 效能測試系統

## 快速開始

```bash
# 編譯所有程式
make build

# 啟動 server
make server

# 執行測試
make test

# 清理編譯檔案
make clean
```

## 測試結果

| 客戶端 | 吞吐量 (req/s) | 平均延遲 (ms) | P99 延遲 (ms) |
|--------|----------------|---------------|---------------|
| Rust   | 91,430         | 1.07          | 1.54          |
| C++    | 24,813         | 0.27          | 1.40          |
| Python | 12,301         | 206.28        | 233.70        |

## 架構說明

### Server (Rust + Axum)
- 接收訂單請求
- 記錄 client/server 時間戳
- 計算網路延遲

### 客戶端實作
- **Python**: aiohttp 異步框架
- **C++**: libcurl + std::async
- **Rust**: reqwest + tokio

## API 格式

### POST /order
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

### Response
```json
{
  "order_id": "ORDER_001",
  "status": "ACCEPTED",
  "client_timestamp": "2024-01-01T10:00:00.000Z",
  "server_timestamp": "2024-01-01T10:00:00.010Z",
  "latency_ms": 10.0
}
```

## 單獨測試

```bash
# Python
python3 python_client.py --orders 1000 --connections 100

# C++
./build/cpp_client 1000 100 100

# Rust
./rust-client/target/release/rust-client --orders 1000 --connections 100
```

## 效能分析

- **Rust 最快**: 利用 tokio 異步運行時的高效能
- **C++ 延遲最低**: 但並發能力不如 Rust
- **Python 最慢**: GIL 限制，但開發效率高

## 系統需求

- Rust 1.70+
- Python 3.7+
- C++17
- CMake 3.10+
- libcurl-dev