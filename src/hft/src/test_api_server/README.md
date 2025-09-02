# API Performance Testing Suite

This project compares the performance of three different async HTTP clients (Python, C++, Rust) connecting to a Rust-based API server.

## Project Structure

```
test_api_server/
├── rust-api-server/    # Rust API server using Axum
├── rust-client/        # Rust async client using reqwest + tokio
├── python_client.py    # Python async client using aiohttp
├── cpp_client.cpp      # C++ async client using libcurl
├── CMakeLists.txt      # C++ build configuration
└── run_benchmark.sh    # Automated benchmark script
```

## Features

- **Rust API Server**: High-performance async server built with Axum and Tokio
- **Three Client Implementations**:
  - Python with aiohttp (async/await)
  - C++ with libcurl and std::async
  - Rust with reqwest and tokio
- **Latency Tracking**: Measures network round-trip time and server processing time
- **Performance Metrics**: Throughput, latency percentiles (P50, P90, P95, P99)

## Prerequisites

### System Requirements
- Linux/macOS (tested on Ubuntu 20.04+)
- 4+ CPU cores recommended
- 8GB+ RAM recommended

### Software Dependencies

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

## Quick Start

### 1. Start the API Server
```bash
cd rust-api-server
cargo run --release
```
The server will start on `http://localhost:8080`

### 2. Run Individual Clients

#### Python Client
```bash
python3 python_client.py --orders 1000 --connections 100 --warmup 100
```

#### C++ Client
```bash
mkdir build && cd build
cmake .. && make
./cpp_client 1000 100 100
```

#### Rust Client
```bash
cd rust-client
cargo run --release -- --orders 1000 --connections 100 --warmup 100
```

### 3. Run Automated Benchmark
```bash
chmod +x run_benchmark.sh
./run_benchmark.sh
```

## API Endpoints

### POST /order
Submit a trading order with timestamp tracking.

Request:
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

Response:
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
Get server performance statistics.

Response:
```json
{
  "total_orders": 5000,
  "elapsed_seconds": 5.23,
  "orders_per_second": 956.02
}
```

## Performance Metrics Explained

- **Round-trip Latency**: Total time from client request to response
- **Server Latency**: Time difference between client and server timestamps
- **Throughput**: Orders processed per second
- **Percentiles**: P50 (median), P90, P95, P99 latency distribution

## Tuning Parameters

### Client Configuration
- `--orders`: Total number of orders to send
- `--connections`: Number of concurrent connections
- `--warmup`: Number of warmup orders (not counted in stats)

### Server Configuration
Edit `rust-api-server/src/main.rs` to adjust:
- Port number (default: 8080)
- Logging level
- CORS settings

## Expected Results

Typical performance on a modern system (Intel i7, 16GB RAM):

| Client | Throughput (orders/sec) | P50 Latency (ms) | P99 Latency (ms) |
|--------|-------------------------|------------------|------------------|
| Rust   | 15,000-20,000          | 5-10             | 20-30            |
| Python | 5,000-8,000            | 15-25            | 50-80            |
| C++    | 10,000-15,000          | 8-15             | 30-50            |

*Results vary based on system specifications and load*

## Troubleshooting

### Server won't start
- Check if port 8080 is already in use: `lsof -i :8080`
- Kill existing process: `kill -9 <PID>`

### C++ client compilation errors
- Ensure libcurl-dev is installed
- Check CMake version: `cmake --version` (need 3.10+)

### Python client errors
- Install aiohttp: `pip install aiohttp`
- Check Python version: `python3 --version` (need 3.7+)

### Low performance
- Run server in release mode: `cargo run --release`
- Increase file descriptor limits: `ulimit -n 65536`
- Check CPU governor: `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`

## License

MIT