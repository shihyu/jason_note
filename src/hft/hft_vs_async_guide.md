# 高頻交易 vs 異步編程完整指南

## 目錄
1. [異步編程基礎](#異步編程基礎)
2. [並行處理與連線分散](#並行處理與連線分散)
3. [高頻交易的真相](#高頻交易的真相)
4. [技術選擇決策](#技術選擇決策)
5. [實戰案例](#實戰案例)

---

## 異步編程基礎

### async 與多執行緒的區別

#### 傳統多執行緒問題
```python
import threading
import requests

def blocking_api_call(url):
    return requests.get(url)  # 阻塞執行緒

# 問題：每個執行緒消耗 8MB 記憶體
threads = []
for url in urls:
    t = threading.Thread(target=blocking_api_call, args=(url,))
    threads.append(t)
    t.start()
```

#### async 解決方案
```python
import asyncio
import aiohttp

async def non_blocking_api_call(session, url):
    async with session.get(url) as response:
        return await response.text()

# 單執行緒處理大量併發
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [non_blocking_api_call(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
```

### 何時使用 async？

#### ✅ 適合 async 的場景
- **I/O 密集型任務**：網路請求、檔案讀寫、資料庫查詢
- **大量併發連線**：需要同時處理數百至數千個連線
- **延遲容忍度高**：毫秒到秒級的延遲可接受

#### ❌ 不適合 async 的場景
- **CPU 密集型任務**：數學運算、影像處理
- **極低延遲要求**：微秒級響應需求
- **簡單序列處理**：單一任務流程

---

## 並行處理與連線分散

### 連線池原理

#### 問題：單一連線的瓶頸
```
傳統方式每次請求：
請求1: TCP握手(100ms) + 請求(50ms) + 回應(50ms) = 200ms
請求2: TCP握手(100ms) + 請求(50ms) + 回應(50ms) = 200ms
總計: 400ms
```

#### 解決方案：連線池
```
連線池方式：
請求1: TCP握手(100ms) + 請求(50ms) + 回應(50ms) = 200ms  
請求2: 重用連線 + 請求(50ms) + 回應(50ms) = 100ms
總計: 300ms，節省 25%
```

### aiohttp 連線配置

```python
import aiohttp
import asyncio

# 高效能連線配置
connector = aiohttp.TCPConnector(
    limit=200,              # 全域連線池大小
    limit_per_host=50,      # 每個 host 最多 50 條連線
    keepalive_timeout=60,   # 連線保持時間
    force_close=False,      # 保持連線重用
    enable_cleanup_closed=True,
    ssl=False              # 內部 API 可關閉 SSL
)

async with aiohttp.ClientSession(connector=connector) as session:
    # aiohttp 自動分散請求到 50 條連線
    tasks = [session.get(url) for url in urls]  # 1000 個請求
    results = await asyncio.gather(*tasks)
```

### 連線分散策略

#### 單一 Session 多連線（推薦）
```python
async def single_session_multiple_connections():
    connector = aiohttp.TCPConnector(limit_per_host=50)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # aiohttp 內建負載均衡，自動分散到 50 條連線
        tasks = [session.get(url) for url in urls]
        results = await asyncio.gather(*tasks)
```

#### 多 Session 手動分散（特殊需求）
```python
async def multiple_sessions_approach():
    sessions = []
    for i in range(5):
        connector = aiohttp.TCPConnector(limit_per_host=10)
        sessions.append(aiohttp.ClientSession(connector=connector))
    
    tasks = []
    for i, url in enumerate(urls):
        session_idx = i % len(sessions)
        tasks.append(sessions[session_idx].get(url))
    
    results = await asyncio.gather(*tasks)
```

### 效能比較表

| 方案 | I/O 密集型 | CPU 密集型 | 記憶體使用 | 複雜度 | 適用場景 |
|------|------------|------------|------------|--------|----------|
| **async + non-blocking API** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | **最佳選擇** |
| **async + run_in_executor** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 混合 blocking API |
| **ThreadPoolExecutor** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 簡單平行處理 |
| **MultiProcessing** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | CPU 密集型任務 |

---

## 高頻交易的真相

### 高頻交易 vs 大量下單

#### 高頻交易（HFT）- 追求極致速度
```cpp
// 市場造市策略
void market_making_strategy() {
    while(trading_active) {
        auto tick = get_market_tick();           // < 1μs
        
        if(spread_too_wide(tick)) {
            cancel_old_quotes();                 // < 1μs
            send_new_quotes();                   // < 1μs
        }
        // 整個循環必須 < 5μs
    }
}
```

**特色：**
- 📈 少量交易，極快速度
- ⚡ 微秒級反應時間
- 🎯 搶奪價差、套利機會

#### 大量下單 - 追求執行數量
```python
# 機構投資批量交易
async def institutional_bulk_trading():
    total_shares = 10_000_000  # 1000萬股
    
    # 分散執行，避免衝擊市價
    for batch in chunk_orders(orders, 50):
        await asyncio.gather(*[send_order(order) for order in batch])
        await asyncio.sleep(1)  # 延遲可接受
```

**特色：**
- 📊 大量交易，適度速度
- ⏱️ 秒級/分鐘級延遲
- 💰 成本控制優先

### 為什麼高頻交易不用 async？

#### 1. 極低延遲需求
```cpp
// 高頻交易的時間要求
Order order;
order.symbol = "AAPL";
market_gateway.send_order(order);  // 必須 < 1 微秒

// async 的問題
async auto process_tick() {
    auto tick = co_await get_tick();    // 可能 0.5μs，也可能 50μs
    co_await send_order();              // 執行時機不可控
}
```

#### 2. 確定性延遲
```cpp
// 高頻交易要求：每次都是相同的低延遲
while(true) {
    auto tick = market_feed.get_next_tick();  // 固定 0.5μs
    strategy.process(tick);                   // 固定 1.2μs  
    if(should_trade) {
        gateway.send_order(order);            // 固定 0.8μs
    }
}
// 總計：2.5μs，每次都一樣
```

#### 3. 協程切換開銷
```cpp
// async 的隱藏成本
auto process_market_data() -> task<void> {
    auto data = co_await get_market_data();     // 切換開銷 ~100ns
    auto signal = co_await calculate_signal();  // 切換開銷 ~100ns
    co_await send_order();                      // 切換開銷 ~100ns
}
// 總開銷：300ns，在高頻交易中是巨大的

// 直接版本
void process_market_data_direct() {
    auto data = market_feed.get_immediate();    // 0ns 切換
    auto signal = strategy.calculate_now(data); // 0ns 切換  
    gateway.send_now(order);                    // 0ns 切換
}
```

### 高頻交易的 CPU Busy 策略

#### 為什麼要讓 CPU 100% 忙碌？

**1. 零切換延遲**
```cpp
// 非 busy 方式：有切換開銷
poll(fd, &events, 1, timeout);  // 系統調用 ~1000ns
// CPU 可能被調度給其他程式，喚醒需要 ~5000ns

// busy 方式：無切換開銷  
while(true) {
    if(*shared_memory_ptr != last_value) {  // 直接記憶體檢查 ~10ns
        process_tick();                     // 立即處理 ~100ns
    }
}
```

**2. CPU 快取保持熱態**
```cpp
class HFTEngine {
    alignas(64) volatile uint64_t market_data[1000];  // L1 cache
    alignas(64) Strategy strategy;                    // 熱態快取
    
public:
    void run() {
        // CPU 100% 專注在這個迴圈
        while(trading_active) {
            // 所有資料都在 L1 cache，超快存取
            auto tick = market_data[read_idx];
            strategy.calculate_immediate(tick);
        }
    }
};
```

#### 實際 Busy Waiting 技巧

**1. 輪詢（Polling）**
```cpp
class UltraLowLatencyNIC {
public:
    void busy_poll_packets() {
        while(true) {
            auto* packet = (Packet*)rx_ring_buffer[rx_head];
            
            if(packet->status == PACKET_READY) {
                process_market_data(packet);
                rx_head = (rx_head + 1) % RING_SIZE;
            }
            // 不 sleep，保持 CPU 100%
        }
    }
};
```

**2. 無鎖資料結構**
```cpp
template<typename T>
class LockFreeQueue {
private:
    alignas(64) std::atomic<uint64_t> head{0};
    alignas(64) std::atomic<uint64_t> tail{0};
    alignas(64) T buffer[SIZE];
    
public:
    bool try_push(const T& item) {
        // 忙等待直到有空間，不阻塞
        uint64_t current_tail = tail.load(std::memory_order_relaxed);
        // ... 無鎖操作
        return true;
    }
};
```

**3. CPU 親和性設定**
```cpp
void setup_cpu_isolation() {
    // 綁定到專用核心
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(2, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
    
    // 設定最高優先級
    struct sched_param param;
    param.sched_priority = 99;
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
}
```

#### 硬體層面優化

**DPDK（繞過 kernel）**
```cpp
void dpdk_busy_poll() {
    while(trading_active) {
        // 直接從網卡 DMA 記憶體讀取
        struct rte_mbuf* packets[BURST_SIZE];
        uint16_t nb_rx = rte_eth_rx_burst(port_id, 0, packets, BURST_SIZE);
        
        for(int i = 0; i < nb_rx; i++) {
            process_packet_immediate(packets[i]);
        }
        // CPU 始終 100%，不讓給任何其他程式
    }
}
```

**系統配置**
```bash
# 核心隔離
GRUB_CMDLINE_LINUX="isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3"

# CPU 調節器
echo performance > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor
```

---

## 技術選擇決策

### 決策樹

```
是否為 I/O 密集型？
├─ 是
│  ├─ 延遲要求 < 10μs？
│  │  ├─ 是 → C++ 同步 + busy waiting
│  │  └─ 否 → async + aiohttp
│  └─ 大量並行需求？
│     ├─ 是 → async + connector
│     └─ 否 → 簡單同步
└─ 否（CPU 密集型）
   ├─ 需要並行？
   │  ├─ 是 → multiprocessing
   │  └─ 否 → 單執行緒
   └─ 極致性能？ → C++ + SIMD
```

### 場景對應表

| 場景 | 技術選擇 | 原因 | 延遲 |
|------|----------|------|------|
| **高頻交易** | C++ 同步 + busy waiting | 確定性延遲、CPU 專用 | < 10μs |
| **大量 API 請求** | async + aiohttp | I/O 密集、高併發 | < 100ms |
| **機構批量下單** | async + connector | 大量 I/O、成本控制 | < 1s |
| **數據分析** | multiprocessing | CPU 密集、可並行 | 不重要 |
| **簡單腳本** | requests | 簡單易用 | < 10s |

---

## 實戰案例

### 案例1：券商批量下單系統

#### 需求分析
- 開盤時快速下單 100+ 筆訂單
- 延遲容忍度：秒級
- 主要瓶頸：網路 I/O

#### 技術選擇：async + aiohttp
```python
class AsyncFubonTrader:
    def __init__(self, max_workers=50):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            keepalive_timeout=60
        )
    
    async def batch_buy_stock(self, symbol, batch_count, quantity_per_batch):
        def _batch_order():
            orders = [create_order(...) for i in range(batch_count)]
            return self.sdk.stock.batch_place_order(self.account, orders)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, _batch_order)
        return result
```

#### 開盤搶單優化
```python
class OpeningRushTrader:
    async def ultra_fast_batch_send(self, chunk_size=10, delay_ms=50):
        # 分批發送避免壓垮系統
        chunks = [orders[i:i + chunk_size] for i in range(0, len(orders), chunk_size)]
        
        tasks = []
        for i, chunk in enumerate(chunks):
            task = self.send_chunk(chunk, i+1)
            tasks.append(task)
            
            # 小延遲避免過載
            if delay_ms > 0 and i < len(chunks) - 1:
                await asyncio.sleep(delay_ms / 1000)
        
        results = await asyncio.gather(*tasks)
        return results
```

### 案例2：市場數據處理對比

#### 高頻交易版本
```cpp
// 專業交易公司的做法
class MarketDataProcessor {
    void run() {
        // 綁定專用 CPU 核心
        bind_to_cpu(2);
        
        while(trading_active) {
            // 忙等待市場數據
            auto tick = get_tick_immediate();
            
            if(arbitrage_opportunity(tick)) {
                send_order_immediate();  // < 1μs
            }
        }
    }
};
```

#### 一般交易系統版本
```python
# 個人/小機構的做法
async def market_data_processor():
    async with aiohttp.ClientSession() as session:
        while True:
            # 查詢市場數據
            tick = await get_market_tick(session)
            
            # 分析機會（可等待）
            if await analyze_opportunity(tick):
                await send_order(session, order)
            
            await asyncio.sleep(0.1)  # 100ms 間隔可接受
```

### 案例3：時間比較系統

#### 實時延遲監控
```python
def _print_time_comparison(self, order_history, query_time):
    for i, order in enumerate(order_history, 1):
        last_time_str = getattr(order, 'last_time', None)
        if last_time_str:
            # 計算延遲
            order_time = datetime.strptime(f"{today} {last_time_str}", "%Y-%m-%d %H:%M:%S.%f")
            time_diff = query_time - order_time
            diff_ms = abs(time_diff.total_seconds() * 1000)
            
            # 延遲分級
            status = "🟢 即時" if diff_ms < 1000 else \
                    "🟡 延遲" if diff_ms < 5000 else \
                    "🔴 嚴重延遲"
            
            print(f"委託時間: {last_time_str}")
            print(f"本地時間: {query_time.strftime('%H:%M:%S.%f')[:-3]}")
            print(f"時間差異: {diff_ms:.1f}ms {status}")
```

### 案例4：多策略並行下單
```python
async def execute_multiple_strategies(self, strategies: Dict[str, List[OrderBatch]]):
    async def execute_strategy(name, order_batches):
        self.prepare_orders(order_batches)
        results = await self.ultra_fast_batch_send(chunk_size=3, delay_ms=5)
        return name, results
    
    # 所有策略並行執行
    tasks = [
        execute_strategy(name, batches) 
        for name, batches in strategies.items()
    ]
    
    strategy_results = await asyncio.gather(*tasks)
    return strategy_results
```

---

## 總結與建議

### 核心原則

1. **明確需求**
   - 延遲要求：微秒級 → C++，毫秒級 → async
   - 吞吐量需求：大量 I/O → async，CPU 密集 → multiprocessing
   - 確定性要求：高 → 同步，低 → async

2. **技術選型**
   - 高頻交易：C++ + busy waiting + 專用硬體
   - 大量下單：async + aiohttp + connector
   - 數據處理：根據 I/O vs CPU 比例選擇

3. **效能優化**
   - 連線池配置：根據目標服務器調整
   - 批次大小：平衡延遲與吞吐量
   - 錯誤處理：避免單點故障影響整體性能

### 最佳實踐

```python
# 券商交易系統推薦配置
connector = aiohttp.TCPConnector(
    limit=200,                    # 總連線數
    limit_per_host=50,           # 單券商連線數
    keepalive_timeout=300,       # 保持連線
    force_close=False,
    tcp_keepalive=True
)

# 執行緒池配置
max_workers = min(50, (len(orders) // 10) + 5)

# 批次策略
chunk_size = 5                   # 每批 5 筆訂單
delay_ms = 10                    # 批次間 10ms 延遲
```

### 未來發展趨向

1. **硬體加速**：FPGA、GPU 在金融交易中的應用
2. **邊緣計算**：接近交易所的部署策略
3. **機器學習**：實時決策與風險控制
4. **量子通訊**：未來的超低延遲通訊技術

---

**記住：選擇正確的技術比優化錯誤的技術更重要！**
