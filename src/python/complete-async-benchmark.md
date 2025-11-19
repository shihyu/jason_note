# 完整 Async API 效能測試指南

## 目錄
1. [測試架構概述](#測試架構概述)
2. [Server 端實作](#server-端實作)
3. [Client 端實作](#client-端實作)
4. [環境設置](#環境設置)
5. [執行測試](#執行測試)
6. [效能分析](#效能分析)

## 測試架構概述

### 測試目標
比較 Python、C++、Rust 三種語言的 async HTTP client 在下單 API 場景中的效能表現。

### 關鍵指標
- **Round Trip Time (RTT)**: Client 發送請求到收到回應的總時間
- **Server Latency**: Server 收到請求時間 - Client 發送時間
- **Throughput**: 每秒處理的請求數 (RPS)
- **P50/P95/P99 延遲**: 延遲分佈的百分位數

### 測試參數
- 總請求數: 1000-10000
- 並發數: 50-200
- Payload 大小: ~200 bytes (模擬真實下單資料)

---

## Server 端實作

### 選項 1: Rust Server (Actix-web) 【推薦】

#### Cargo.toml
```toml
[package]
name = "rust_server"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "4"
tokio = { version = "1", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
chrono = "0.4"
env_logger = "0.11"
```

#### src/main.rs
```rust
use actix_web::{web, App, HttpServer, HttpResponse, middleware};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

#[derive(Deserialize)]
struct Order {
    order_id: String,
    symbol: String,
    quantity: i32,
    price: f64,
    timestamp: u128,
}

#[derive(Serialize)]
struct OrderResponse {
    status: String,
    order_id: String,
    server_receive_time: u128,
    client_send_time: u128,
    latency_ns: i128,
}

struct AppState {
    request_count: AtomicUsize,
}

async fn place_order(
    order: web::Json<Order>,
    data: web::Data<Arc<AppState>>,
) -> HttpResponse {
    let server_receive_time = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    
    data.request_count.fetch_add(1, Ordering::SeqCst);
    
    let latency_ns = server_receive_time as i128 - order.timestamp as i128;
    
    let response = OrderResponse {
        status: "success".to_string(),
        order_id: order.order_id.clone(),
        server_receive_time,
        client_send_time: order.timestamp,
        latency_ns,
    };
    
    HttpResponse::Ok().json(response)
}

async fn get_stats(data: web::Data<Arc<AppState>>) -> HttpResponse {
    let count = data.request_count.load(Ordering::SeqCst);
    HttpResponse::Ok().json(serde_json::json!({
        "total_requests": count
    }))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("warn"));
    
    println!("Starting Rust server on port 8000...");
    
    let app_state = Arc::new(AppState {
        request_count: AtomicUsize::new(0),
    });
    
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(app_state.clone()))
            .route("/order", web::post().to(place_order))
            .route("/stats", web::get().to(get_stats))
    })
    .workers(8)
    .bind("0.0.0.0:8000")?
    .run()
    .await
}
```

### 選項 2: Go Server (Gin)

#### go.mod
```go
module server

go 1.21

require github.com/gin-gonic/gin v1.9.1
```

#### server.go
```go
package main

import (
    "fmt"
    "net/http"
    "sync/atomic"
    "time"
    
    "github.com/gin-gonic/gin"
)

type Order struct {
    OrderID   string  `json:"order_id"`
    Symbol    string  `json:"symbol"`
    Quantity  int     `json:"quantity"`
    Price     float64 `json:"price"`
    Timestamp int64   `json:"timestamp"`
}

type OrderResponse struct {
    Status           string `json:"status"`
    OrderID          string `json:"order_id"`
    ServerReceiveTime int64  `json:"server_receive_time"`
    ClientSendTime   int64  `json:"client_send_time"`
    LatencyNs        int64  `json:"latency_ns"`
}

var requestCount uint64

func placeOrder(c *gin.Context) {
    var order Order
    
    if err := c.ShouldBindJSON(&order); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    
    serverReceiveTime := time.Now().UnixNano()
    atomic.AddUint64(&requestCount, 1)
    latencyNs := serverReceiveTime - order.Timestamp
    
    response := OrderResponse{
        Status:            "success",
        OrderID:           order.OrderID,
        ServerReceiveTime: serverReceiveTime,
        ClientSendTime:    order.Timestamp,
        LatencyNs:         latencyNs,
    }
    
    c.JSON(http.StatusOK, response)
}

func getStats(c *gin.Context) {
    count := atomic.LoadUint64(&requestCount)
    c.JSON(http.StatusOK, gin.H{
        "total_requests": count,
    })
}

func main() {
    gin.SetMode(gin.ReleaseMode)
    
    r := gin.New()
    r.Use(gin.Recovery())
    
    r.POST("/order", placeOrder)
    r.GET("/stats", getStats)
    
    fmt.Println("Starting Go server on port 8000...")
    r.Run(":8000")
}
```

### 選項 3: Python Server (FastAPI + uvloop) 【備用】

#### requirements.txt
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
uvloop==0.19.0
pydantic==2.5.0
```

#### optimized_server.py
```python
import asyncio
import uvloop
import multiprocessing
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import time

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI()

class Order(BaseModel):
    order_id: str
    symbol: str
    quantity: int
    price: float
    timestamp: int

@app.post("/order")
async def place_order(order: Order):
    server_receive_time = time.time_ns()
    
    return {
        "status": "success",
        "order_id": order.order_id,
        "server_receive_time": server_receive_time,
        "client_send_time": order.timestamp,
        "latency_ns": server_receive_time - order.timestamp
    }

@app.get("/stats")
async def get_stats():
    return {"status": "ok"}

if __name__ == "__main__":
    workers = multiprocessing.cpu_count()
    
    uvicorn.run(
        "optimized_server:app",
        host="0.0.0.0",
        port=8000,
        workers=workers,
        loop="uvloop",
        log_level="warning",
        access_log=False
    )
```

---

## Client 端實作

### Python Client

#### requirements.txt
```
aiohttp==3.9.0
asyncio==3.4.3
```

#### python_client.py
```python
import asyncio
import aiohttp
import time
import json
from typing import List
import statistics

class PythonBenchmark:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def send_order(self, session: aiohttp.ClientSession, order_id: int):
        order = {
            "order_id": f"PY_{order_id}",
            "symbol": "AAPL",
            "quantity": 100,
            "price": 150.25,
            "timestamp": time.time_ns()
        }
        
        start = time.time_ns()
        try:
            async with session.post(f'{self.base_url}/order', json=order) as response:
                result = await response.json()
                end = time.time_ns()
                
                return {
                    "round_trip_ns": end - start,
                    "server_latency_ns": result["latency_ns"],
                    "success": True
                }
        except Exception as e:
            return {
                "round_trip_ns": 0,
                "server_latency_ns": 0,
                "success": False,
                "error": str(e)
            }
    
    async def benchmark(self, num_requests: int = 1000, concurrent: int = 100):
        connector = aiohttp.TCPConnector(limit=concurrent, force_close=True)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            all_results = []
            
            for i in range(num_requests):
                task = self.send_order(session, i)
                tasks.append(task)
                
                if len(tasks) >= concurrent:
                    results = await asyncio.gather(*tasks)
                    all_results.extend(results)
                    tasks = []
            
            if tasks:
                results = await asyncio.gather(*tasks)
                all_results.extend(results)
        
        return all_results
    
    def print_stats(self, results: List[dict], duration: float):
        successful = [r for r in results if r["success"]]
        failed = len(results) - len(successful)
        
        if not successful:
            print("All requests failed!")
            return
        
        round_trips = [r["round_trip_ns"] for r in successful]
        server_latencies = [r["server_latency_ns"] for r in successful]
        
        round_trips.sort()
        server_latencies.sort()
        
        print(f"\n{'='*50}")
        print(f"Python Client Results")
        print(f"{'='*50}")
        print(f"Total Time: {duration:.2f}s")
        print(f"Total Requests: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {failed}")
        print(f"Throughput: {len(successful)/duration:.2f} req/s")
        print(f"\nRound Trip Time:")
        print(f"  Average: {statistics.mean(round_trips)/1e6:.2f}ms")
        print(f"  P50: {round_trips[len(round_trips)//2]/1e6:.2f}ms")
        print(f"  P95: {round_trips[int(len(round_trips)*0.95)]/1e6:.2f}ms")
        print(f"  P99: {round_trips[int(len(round_trips)*0.99)]/1e6:.2f}ms")
        print(f"\nServer Latency:")
        print(f"  Average: {statistics.mean(server_latencies)/1e6:.2f}ms")

async def main():
    benchmark = PythonBenchmark()
    
    print("Python Client Benchmark Starting...")
    print("Warming up...")
    await benchmark.benchmark(num_requests=100, concurrent=10)
    
    print("Running benchmark...")
    start_time = time.time()
    results = await benchmark.benchmark(num_requests=5000, concurrent=100)
    duration = time.time() - start_time
    
    benchmark.print_stats(results, duration)

if __name__ == "__main__":
    asyncio.run(main())
```

### C++ Client

#### CMakeLists.txt
```cmake
cmake_minimum_required(VERSION 3.10)
project(cpp_client)

set(CMAKE_CXX_STANDARD 17)

find_package(Threads REQUIRED)

# 使用 vcpkg 或手動安裝這些庫
find_package(cpr CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

add_executable(cpp_client cpp_client.cpp)
target_link_libraries(cpp_client 
    PRIVATE 
    cpr::cpr 
    nlohmann_json::nlohmann_json 
    Threads::Threads
)
```

#### cpp_client.cpp
```cpp
#include <iostream>
#include <chrono>
#include <vector>
#include <future>
#include <algorithm>
#include <numeric>
#include <thread>
#include <cpr/cpr.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace std::chrono;

struct Result {
    long long round_trip_ns;
    long long server_latency_ns;
    bool success;
};

class CppBenchmark {
private:
    std::string base_url;
    
public:
    CppBenchmark(const std::string& url = "http://localhost:8000") 
        : base_url(url) {}
    
    Result send_order(int order_id) {
        auto now = duration_cast<nanoseconds>(
            system_clock::now().time_since_epoch()
        ).count();
        
        json order;
        order["order_id"] = "CPP_" + std::to_string(order_id);
        order["symbol"] = "AAPL";
        order["quantity"] = 100;
        order["price"] = 150.25;
        order["timestamp"] = now;
        
        auto start = high_resolution_clock::now();
        
        try {
            auto response = cpr::Post(
                cpr::Url{base_url + "/order"},
                cpr::Header{{"Content-Type", "application/json"}},
                cpr::Body{order.dump()}
            );
            
            auto end = high_resolution_clock::now();
            auto round_trip = duration_cast<nanoseconds>(end - start).count();
            
            if (response.status_code == 200) {
                json resp_json = json::parse(response.text);
                return {
                    round_trip,
                    resp_json["latency_ns"],
                    true
                };
            }
        } catch (const std::exception& e) {
            // Handle error
        }
        
        return {0, 0, false};
    }
    
    std::vector<Result> benchmark(int num_requests, int concurrent) {
        std::vector<std::future<Result>> futures;
        std::vector<Result> results;
        
        for (int i = 0; i < num_requests; i++) {
            futures.push_back(
                std::async(std::launch::async, 
                    &CppBenchmark::send_order, this, i)
            );
            
            if (futures.size() >= concurrent) {
                for (auto& f : futures) {
                    results.push_back(f.get());
                }
                futures.clear();
            }
        }
        
        for (auto& f : futures) {
            results.push_back(f.get());
        }
        
        return results;
    }
    
    void print_stats(const std::vector<Result>& results, double duration) {
        std::vector<Result> successful;
        std::copy_if(results.begin(), results.end(), 
            std::back_inserter(successful),
            [](const Result& r) { return r.success; });
        
        if (successful.empty()) {
            std::cout << "All requests failed!" << std::endl;
            return;
        }
        
        std::vector<long long> round_trips;
        std::vector<long long> server_latencies;
        
        for (const auto& r : successful) {
            round_trips.push_back(r.round_trip_ns);
            server_latencies.push_back(r.server_latency_ns);
        }
        
        std::sort(round_trips.begin(), round_trips.end());
        std::sort(server_latencies.begin(), server_latencies.end());
        
        double avg_rt = std::accumulate(round_trips.begin(), 
            round_trips.end(), 0.0) / round_trips.size();
        double avg_sl = std::accumulate(server_latencies.begin(), 
            server_latencies.end(), 0.0) / server_latencies.size();
        
        std::cout << "\n==================================================" << std::endl;
        std::cout << "C++ Client Results" << std::endl;
        std::cout << "==================================================" << std::endl;
        std::cout << "Total Time: " << duration << "s" << std::endl;
        std::cout << "Total Requests: " << results.size() << std::endl;
        std::cout << "Successful: " << successful.size() << std::endl;
        std::cout << "Failed: " << results.size() - successful.size() << std::endl;
        std::cout << "Throughput: " << successful.size() / duration << " req/s" << std::endl;
        std::cout << "\nRound Trip Time:" << std::endl;
        std::cout << "  Average: " << avg_rt / 1e6 << "ms" << std::endl;
        std::cout << "  P50: " << round_trips[round_trips.size()/2] / 1e6 << "ms" << std::endl;
        std::cout << "  P95: " << round_trips[round_trips.size()*95/100] / 1e6 << "ms" << std::endl;
        std::cout << "  P99: " << round_trips[round_trips.size()*99/100] / 1e6 << "ms" << std::endl;
        std::cout << "\nServer Latency:" << std::endl;
        std::cout << "  Average: " << avg_sl / 1e6 << "ms" << std::endl;
    }
};

int main() {
    CppBenchmark benchmark;
    
    std::cout << "C++ Client Benchmark Starting..." << std::endl;
    std::cout << "Warming up..." << std::endl;
    benchmark.benchmark(100, 10);
    
    std::cout << "Running benchmark..." << std::endl;
    auto start = high_resolution_clock::now();
    auto results = benchmark.benchmark(5000, 100);
    auto end = high_resolution_clock::now();
    
    double duration = duration_cast<milliseconds>(end - start).count() / 1000.0;
    benchmark.print_stats(results, duration);
    
    return 0;
}
```

### Rust Client

#### Cargo.toml
```toml
[package]
name = "rust_client"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1", features = ["full"] }
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
futures = "0.3"
```

#### src/main.rs
```rust
use reqwest;
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH, Instant};
use tokio;
use futures::future::join_all;

#[derive(Serialize, Deserialize)]
struct Order {
    order_id: String,
    symbol: String,
    quantity: i32,
    price: f64,
    timestamp: u128,
}

#[derive(Deserialize)]
struct OrderResponse {
    status: String,
    order_id: String,
    server_receive_time: u128,
    client_send_time: u128,
    latency_ns: i128,
}

#[derive(Debug, Clone)]
struct Result {
    round_trip_ns: u128,
    server_latency_ns: i128,
    success: bool,
}

struct RustBenchmark {
    base_url: String,
    client: reqwest::Client,
}

impl RustBenchmark {
    fn new(base_url: &str) -> Self {
        let client = reqwest::Client::builder()
            .pool_max_idle_per_host(200)
            .build()
            .unwrap();
        
        Self {
            base_url: base_url.to_string(),
            client,
        }
    }
    
    async fn send_order(&self, order_id: i32) -> Result {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        
        let order = Order {
            order_id: format!("RUST_{}", order_id),
            symbol: "AAPL".to_string(),
            quantity: 100,
            price: 150.25,
            timestamp,
        };
        
        let start = Instant::now();
        
        match self.client
            .post(format!("{}/order", self.base_url))
            .json(&order)
            .send()
            .await
        {
            Ok(response) => {
                match response.json::<OrderResponse>().await {
                    Ok(resp) => {
                        let round_trip = start.elapsed().as_nanos();
                        Result {
                            round_trip_ns: round_trip,
                            server_latency_ns: resp.latency_ns,
                            success: true,
                        }
                    }
                    Err(_) => Result {
                        round_trip_ns: 0,
                        server_latency_ns: 0,
                        success: false,
                    }
                }
            }
            Err(_) => Result {
                round_trip_ns: 0,
                server_latency_ns: 0,
                success: false,
            }
        }
    }
    
    async fn benchmark(&self, num_requests: usize, concurrent: usize) -> Vec<Result> {
        let mut tasks = Vec::new();
        let mut all_results = Vec::new();
        
        for i in 0..num_requests {
            let task = self.send_order(i as i32);
            tasks.push(task);
            
            if tasks.len() >= concurrent {
                let results = join_all(tasks).await;
                all_results.extend(results);
                tasks = Vec::new();
            }
        }
        
        if !tasks.is_empty() {
            let results = join_all(tasks).await;
            all_results.extend(results);
        }
        
        all_results
    }
    
    fn print_stats(&self, results: &[Result], duration: f64) {
        let successful: Vec<&Result> = results.iter()
            .filter(|r| r.success)
            .collect();
        
        if successful.is_empty() {
            println!("All requests failed!");
            return;
        }
        
        let mut round_trips: Vec<u128> = successful.iter()
            .map(|r| r.round_trip_ns)
            .collect();
        let mut server_latencies: Vec<i128> = successful.iter()
            .map(|r| r.server_latency_ns)
            .collect();
        
        round_trips.sort();
        server_latencies.sort();
        
        let avg_rt = round_trips.iter().sum::<u128>() as f64 / round_trips.len() as f64;
        let avg_sl = server_latencies.iter().sum::<i128>() as f64 / server_latencies.len() as f64;
        
        println!("\n{}", "=".repeat(50));
        println!("Rust Client Results");
        println!("{}", "=".repeat(50));
        println!("Total Time: {:.2}s", duration);
        println!("Total Requests: {}", results.len());
        println!("Successful: {}", successful.len());
        println!("Failed: {}", results.len() - successful.len());
        println!("Throughput: {:.2} req/s", successful.len() as f64 / duration);
        println!("\nRound Trip Time:");
        println!("  Average: {:.2}ms", avg_rt / 1e6);
        println!("  P50: {:.2}ms", round_trips[round_trips.len()/2] as f64 / 1e6);
        println!("  P95: {:.2}ms", round_trips[round_trips.len()*95/100] as f64 / 1e6);
        println!("  P99: {:.2}ms", round_trips[round_trips.len()*99/100] as f64 / 1e6);
        println!("\nServer Latency:");
        println!("  Average: {:.2}ms", avg_sl / 1e6);
    }
}

#[tokio::main]
async fn main() {
    let benchmark = RustBenchmark::new("http://localhost:8000");
    
    println!("Rust Client Benchmark Starting...");
    println!("Warming up...");
    let _ = benchmark.benchmark(100, 10).await;
    
    println!("Running benchmark...");
    let start = Instant::now();
    let results = benchmark.benchmark(5000, 100).await;
    let duration = start.elapsed().as_secs_f64();
    
    benchmark.print_stats(&results, duration);
}
```

---

## 環境設置

### 系統優化

#### Linux 系統優化 (Ubuntu/Debian)
```bash
# 增加文件描述符限制
sudo bash -c 'echo "* soft nofile 65535" >> /etc/security/limits.conf'
sudo bash -c 'echo "* hard nofile 65535" >> /etc/security/limits.conf'

# TCP 優化
sudo sysctl -w net.core.somaxconn=65535
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=65535
sudo sysctl -w net.ipv4.ip_local_port_range="1024 65535"
sudo sysctl -w net.ipv4.tcp_tw_reuse=1

# 永久保存
sudo bash -c 'echo "net.core.somaxconn=65535" >> /etc/sysctl.conf'
sudo bash -c 'echo "net.ipv4.tcp_max_syn_backlog=65535" >> /etc/sysctl.conf'
```

### 依賴安裝

#### Python 環境
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Rust 環境
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

#### C++ 環境 (使用 vcpkg)
```bash
# 安裝 vcpkg
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.sh
./vcpkg integrate install

# 安裝依賴
./vcpkg install cpr nlohmann-json
```

#### Go 環境
```bash
# 下載並安裝 Go
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

---

## 執行測試

### 自動化測試腳本

#### run_complete_benchmark.sh
```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NUM_REQUESTS=5000
CONCURRENT=100
WARMUP_REQUESTS=100

echo -e "${GREEN}=== Complete Async API Benchmark ===${NC}"
echo "Configuration:"
echo "  Requests: $NUM_REQUESTS"
echo "  Concurrent: $CONCURRENT"
echo ""

# Function to check if port is in use
check_port() {
    lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null
}

# Function to wait for server
wait_for_server() {
    echo -n "Waiting for server to start"
    for i in {1..30}; do
        if curl -s http://localhost:8000/stats > /dev/null; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

# Function to run client benchmark
run_client() {
    local client_name=$1
    local client_cmd=$2
    
    echo -e "\n${YELLOW}Testing $client_name Client...${NC}"
    eval $client_cmd
}

# Kill any existing server
if check_port; then
    echo "Killing existing server on port 8000..."
    kill $(lsof -Pi :8000 -sTCP:LISTEN -t)
    sleep 2
fi

# Test with different servers
servers=("rust" "go" "python")

for server in "${servers[@]}"; do
    echo -e "\n${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}Testing with $server server${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    
    # Start server
    case $server in
        "rust")
            echo "Building and starting Rust server..."
            cd rust_server && cargo build --release
            ./target/release/rust_server &
            ;;
        "go")
            echo "Building and starting Go server..."
            cd go_server && go build
            ./server &
            ;;
        "python")
            echo "Starting Python server..."
            python3 optimized_server.py &
            ;;
    esac
    
    SERVER_PID=$!
    cd ..
    
    # Wait for server to be ready
    if ! wait_for_server; then
        echo -e "${RED}Server failed to start!${NC}"
        kill $SERVER_PID 2>/dev/null
        continue
    fi
    
    # Run all clients
    run_client "Python" "python3 python_client.py"
    run_client "C++" "./cpp_client/build/cpp_client"
    run_client "Rust" "cd rust_client && cargo run --release && cd .."
    
    # Get server stats
    echo -e "\n${YELLOW}Server Stats:${NC}"
    curl -s http://localhost:8000/stats | jq .
    
    # Stop server
    echo -e "\nStopping server..."
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null
    
    sleep 2
done

echo -e "\n${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Benchmark Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
```

### 單獨測試腳本

#### test_single.sh
```bash
#!/bin/bash

SERVER=$1
CLIENT=$2

if [ -z "$SERVER" ] || [ -z "$CLIENT" ]; then
    echo "Usage: ./test_single.sh [rust|go|python] [rust|cpp|python]"
    exit 1
fi

# Start server
case $SERVER in
    "rust")
        cd rust_server && cargo run --release &
        ;;
    "go")
        cd go_server && go run server.go &
        ;;
    "python")
        python3 optimized_server.py &
        ;;
esac

SERVER_PID=$!
sleep 3

# Run client
case $CLIENT in
    "rust")
        cd rust_client && cargo run --release
        ;;
    "cpp")
        ./cpp_client/build/cpp_client
        ;;
    "python")
        python3 python_client.py
        ;;
esac

kill $SERVER_PID
```

---

## 效能分析

### 預期效能結果

#### Server 效能比較
| Server | 延遲 (P50) | 延遲 (P99) | 最大 RPS | CPU 使用率 |
|--------|-----------|-----------|----------|-----------|
| Rust   | 10-30μs   | 50-100μs  | 100k+    | 30-50%    |
| Go     | 20-50μs   | 100-200μs | 50k+     | 40-60%    |
| Python | 100-300μs | 500-1000μs| 10k+     | 70-90%    |

#### Client 效能比較
| Client | 延遲 (P50) | 延遲 (P99) | 並發能力 | 記憶體使用 |
|--------|-----------|-----------|---------|-----------|
| Rust   | 0.5-2ms   | 5-10ms    | 極高     | 低        |
| C++    | 0.8-3ms   | 8-15ms    | 高       | 低        |
| Python | 2-8ms     | 15-30ms   | 中       | 高        |

### 效能監控工具

#### 系統監控
```bash
# CPU 和記憶體監控
htop

# 網路連線監控
netstat -an | grep :8000 | wc -l

# IO 監控
iotop

# 詳細系統資訊
dstat -tcmndylp
```

#### 壓力測試工具
```bash
# 使用 wrk 測試 server 極限
wrk -t12 -c400 -d30s --latency \
    -s post.lua \
    http://localhost:8000/order

# post.lua 內容
cat > post.lua << 'EOF'
wrk.method = "POST"
wrk.body = '{"order_id":"TEST_1","symbol":"AAPL","quantity":100,"price":150.25,"timestamp":1234567890}'
wrk.headers["Content-Type"] = "application/json"
EOF

# 使用 ab 測試
ab -n 10000 -c 100 -p order.json -T application/json \
    http://localhost:8000/order
```

### 結果分析要點

1. **延遲分析**
   - Round Trip Time = 網路延遲 + Server 處理時間 + Client 處理時間
   - Server Latency 主要反映網路延遲
   - 差值反映 Client 和 Server 的處理效率

2. **吞吐量分析**
   - RPS (Requests Per Second) 越高越好
   - 注意觀察是否達到瓶頸（CPU、網路、連線數）

3. **穩定性分析**
   - P99 與 P50 的差距反映系統穩定性
   - 差距越小表示效能越穩定

4. **資源使用分析**
   - CPU 使用率不應超過 80%
   - 記憶體應保持穩定，無洩漏
   - 檔案描述符使用量要在限制內

### 優化建議

#### 通用優化
1. **連線池管理**
   - 適當的連線池大小
   - Keep-alive 連線重用
   - 連線超時設定

2. **並發控制**
   - 根據 CPU 核心數調整並發
   - 使用背壓(backpressure)機制
   - 避免過度並發導致效能下降

3. **協議優化**
   - 考慮使用 HTTP/2
   - 使用二進位協議（如 gRPC）
   - 減少 payload 大小

#### 語言特定優化

**Python:**
- 使用 uvloop 替代默認 event loop
- 考慮 PyPy 或 Cython
- 使用 httpx 替代 aiohttp

**Rust:**
- 調整 tokio runtime workers
- 使用 hyper 直接操作
- 啟用 LTO (Link Time Optimization)

**C++:**
- 使用 jemalloc 或 tcmalloc
- 編譯器優化 flags (-O3, -march=native)
- 考慮使用 boost.beast

### 故障排除

#### 常見問題
1. **"Too many open files" 錯誤**
   ```bash
   ulimit -n 65535
   ```

2. **連線被拒絕**
   - 檢查 server 是否啟動
   - 檢查防火牆設定
   - 確認 port 沒被佔用

3. **高延遲**
   - 檢查 CPU 使用率
   - 檢查網路延遲
   - 調整並發數

4. **記憶體洩漏**
   - 使用 valgrind (C++)
   - 使用 memory profiler (Python)
   - 使用 heaptrack (Rust)

---

## 總結

這個完整的測試框架可以幫助你：

1. **準確測量**三種語言的 async HTTP client 效能
2. **避免 server 成為瓶頸**，確保測試結果反映 client 真實效能
3. **全面的指標**包括延遲、吞吐量、穩定性
4. **可重複執行**的自動化測試流程

根據測試結果，你可以為不同場景選擇最適合的語言：
- **Rust**: 最高效能，適合高頻交易
- **C++**: 高效能，適合既有 C++ 系統整合
- **Python**: 開發快速，適合原型開發和中低頻交易